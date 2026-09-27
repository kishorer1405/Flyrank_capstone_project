from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.submissions import SubmissionRepository
from app.services.dashboard import DashboardService
router=APIRouter(prefix="/api/v1/dashboard",tags=["dashboard"])
repo=SubmissionRepository(); service=DashboardService()
@router.get("/submissions")
def submissions(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0),db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    rows=repo.list_for_tenant(db,user.id,limit,offset)
    return {"items":[{"id":str(x.id),"widget_id":str(x.widget_id),"data":x.data,"country":x.country,"city":x.city,"geo_provider":x.geo_provider,"created_at":x.created_at.isoformat()} for x in rows],"total":repo.count_for_tenant(db,user.id)}
@router.get("/stats")
def stats(db:Session=Depends(get_db),user:User=Depends(get_current_user)): return service.stats(db,user.id)
