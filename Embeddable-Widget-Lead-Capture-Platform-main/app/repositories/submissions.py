import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.submission import Submission
class SubmissionRepository:
    def get_by_idempotency(self, db: Session, widget_id: uuid.UUID, key: str):
        return db.scalar(select(Submission).where(Submission.widget_id == widget_id, Submission.idempotency_key == key))
    def list_for_tenant(self, db: Session, tenant_id: uuid.UUID, limit: int, offset: int):
        return list(db.scalars(select(Submission).where(Submission.tenant_id == tenant_id).order_by(Submission.created_at.desc()).limit(limit).offset(offset)))
    def count_for_tenant(self, db: Session, tenant_id: uuid.UUID):
        return db.scalar(select(func.count()).select_from(Submission).where(Submission.tenant_id == tenant_id)) or 0
