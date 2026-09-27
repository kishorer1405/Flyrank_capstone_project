import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.widget import Widget
class WidgetRepository:
    def list_for_tenant(self, db: Session, tenant_id: uuid.UUID):
        return list(db.scalars(select(Widget).where(Widget.tenant_id == tenant_id).order_by(Widget.created_at.desc())))
    def get_for_tenant(self, db: Session, widget_id: uuid.UUID, tenant_id: uuid.UUID):
        return db.scalar(select(Widget).where(Widget.id == widget_id, Widget.tenant_id == tenant_id))
    def get_public(self, db: Session, widget_id: uuid.UUID):
        return db.scalar(select(Widget).where(Widget.id == widget_id, Widget.is_active.is_(True)))
