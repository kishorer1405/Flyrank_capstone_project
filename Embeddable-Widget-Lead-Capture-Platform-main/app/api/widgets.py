import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.widget import WidgetCreate, WidgetResponse, WidgetUpdate
from app.services.widgets import WidgetService


router = APIRouter(
    prefix="/api/v1/widgets",
    tags=["widgets"],
)

service = WidgetService(get_settings())


def out(w):
    return WidgetResponse(
        **{
            **{
                k: (str(getattr(w, k)) if k == "id" else getattr(w, k))
                for k in [
                    "id",
                    "title",
                    "description",
                    "widget_type",
                    "button_text",
                    "display_options",
                    "is_active",
                    "version",
                ]
            },
            "fields": w.fields,
            "embed_snippet": service.snippet(w),
        }
    )


@router.get("", response_model=list[WidgetResponse])
def list_widgets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return [out(w) for w in service.list(db, user.id)]


@router.post("", response_model=WidgetResponse, status_code=201)
def create_widget(
    payload: WidgetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return out(service.create(db, user.id, payload))


@router.get("/{widget_id}", response_model=WidgetResponse)
def get_widget(
    widget_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return out(service.get(db, user.id, widget_id))


@router.patch("/{widget_id}", response_model=WidgetResponse)
def update_widget(
    widget_id: uuid.UUID,
    payload: WidgetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return out(service.update(db, user.id, widget_id, payload))


@router.delete("/{widget_id}", status_code=204)
def delete_widget(
    widget_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service.delete(db, user.id, widget_id)