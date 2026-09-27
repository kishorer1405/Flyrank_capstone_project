import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.widget import Widget
from app.repositories.widgets import WidgetRepository
from app.schemas.widget import WidgetCreate, WidgetUpdate


class WidgetService:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.repo = WidgetRepository()

    # ========================================================
    # List Widgets
    # ========================================================

    def list(self, db, tenant_id):
        return self.repo.list_for_tenant(
            db,
            tenant_id
        )

    # ========================================================
    # Get Widget
    # ========================================================

    def get(self, db, tenant_id, widget_id):

        w = self.repo.get_for_tenant(
            db,
            widget_id,
            tenant_id
        )

        if not w:
            raise HTTPException(
                404,
                "Widget not found"
            )

        return w

    # ========================================================
    # Create Widget
    # ========================================================

    def create(
        self,
        db: Session,
        tenant_id: uuid.UUID,
        data: WidgetCreate
    ):

        w = Widget(
            tenant_id=tenant_id,
            **data.model_dump()
        )

        w.fields = [
            f.model_dump()
            for f in data.fields
        ]

        db.add(w)
        db.commit()
        db.refresh(w)

        return w

    # ========================================================
    # Update Widget
    # ========================================================

    def update(
        self,
        db,
        tenant_id,
        widget_id,
        data: WidgetUpdate
    ):

        w = self.get(
            db,
            tenant_id,
            widget_id
        )

        values = data.model_dump(
            exclude_unset=True
        )

        if (
            "fields" in values
            and values["fields"] is not None
        ):
            values["fields"] = [
                f.model_dump()
                for f in data.fields
            ]

        for k, v in values.items():
            setattr(w, k, v)

        w.version += 1

        db.commit()
        db.refresh(w)

        return w

    # ========================================================
    # Delete Widget
    # ========================================================

    def delete(
        self,
        db,
        tenant_id,
        widget_id
    ):

        w = self.get(
            db,
            tenant_id,
            widget_id
        )

        db.delete(w)
        db.commit()

    # ========================================================
    # Generate Embed Snippet
    # ========================================================

    def snippet(self, w):
        return (
            f'<script src="{self.settings.widget_script_url}'
            f'?id={w.id}"></script>'
        )