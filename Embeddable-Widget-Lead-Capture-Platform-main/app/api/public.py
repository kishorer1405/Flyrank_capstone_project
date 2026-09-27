import uuid
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.session import get_db
from app.models.widget import Widget
from app.schemas.submission import SubmissionRequest, SubmissionResponse
from app.schemas.widget import PublicWidgetConfig
from app.services.rate_limiter import RateLimiter
from app.services.submissions import SubmissionService
settings=get_settings(); router=APIRouter(prefix="/api/v1/public",tags=["public"])
limiter=RateLimiter(limit=int(settings.rate_limit.split("/")[0]),window_seconds=60)
submission_service=SubmissionService(settings)
@router.get("/widgets/{widget_id}/config",response_model=PublicWidgetConfig)
def public_config(widget_id:uuid.UUID,db:Session=Depends(get_db)):
    w=db.scalar(__import__('sqlalchemy').select(Widget).where(Widget.id==widget_id,Widget.is_active.is_(True)))
    if not w: raise HTTPException(404,"Widget not found")
    return Response(content=PublicWidgetConfig(id=str(w.id),title=w.title,description=w.description,widget_type=w.widget_type,fields=w.fields,button_text=w.button_text,display_options=w.display_options,version=w.version,submission_url=f"{settings.base_url}/api/v1/public/submissions").model_dump_json(),media_type="application/json",headers={"Cache-Control":f"public, max-age={settings.config_cache_seconds}"})
@router.post("/submissions",response_model=SubmissionResponse,status_code=201)
def submit(request:Request,payload:SubmissionRequest,db:Session=Depends(get_db),idempotency_key:str|None=Header(default=None,alias="Idempotency-Key")):
    key=f"{submission_service.client_ip(request)}:{payload.widget_id}"
    if not limiter.allow(key): raise HTTPException(429,"Rate limit exceeded; please try again later")
    submission,duplicate=submission_service.submit(db,request,payload,idempotency_key)
    return SubmissionResponse(id=str(submission.id),status="accepted",message="Submission received successfully",duplicate=duplicate)
@router.options("/submissions")
def submission_options(): return Response(status_code=204)
