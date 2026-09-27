import logging,time
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.job import BackgroundJob
from app.services.side_effect import NotificationService
logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | worker | %(message)s")
settings=get_settings(); notifier=NotificationService(settings)
def process_one(db):
    now=datetime.now(timezone.utc)
    job=db.scalar(select(BackgroundJob).where(BackgroundJob.status.in_(["pending","retry"]),BackgroundJob.available_at<=now).order_by(BackgroundJob.created_at).with_for_update(skip_locked=True))
    if not job:return False
    job.status="running"; job.attempts+=1; db.commit()
    try:
        notifier.send(job.payload); job.status="completed"; job.last_error=None
    except Exception as exc:
        job.last_error=str(exc)
        if job.attempts < job.max_attempts:
            job.status="retry"; job.available_at=now+timedelta(seconds=2**job.attempts); logging.error("Job %s failed; retry %s/%s",job.id,job.attempts,job.max_attempts)
        else:
            job.status="failed"; logging.error("Job %s permanently failed after %s attempts",job.id,job.attempts)
    db.commit();return True
while True:
    db=SessionLocal()
    try:
        if not process_one(db): time.sleep(settings.job_poll_seconds)
    except Exception: logging.exception("Worker loop error"); time.sleep(settings.job_poll_seconds)
    finally: db.close()
