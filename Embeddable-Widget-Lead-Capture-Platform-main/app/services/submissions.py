import ipaddress
import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.job import BackgroundJob
from app.models.submission import Submission
from app.models.widget import Widget
from app.schemas.submission import SubmissionRequest
from app.services.geo import GeoService
from app.repositories.submissions import SubmissionRepository


class SubmissionService:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.repo = SubmissionRepository()
        self.geo = GeoService(settings)

    # ========================================================
    # Get Client IP Address
    # ========================================================

    def client_ip(self, request) -> str:

        forwarded = request.headers.get("x-forwarded-for")

        ip = (
            forwarded.split(",")[0].strip()
            if forwarded
            else (
                request.client.host
                if request.client
                else "0.0.0.0"
            )
        )

        try:
            ipaddress.ip_address(ip)
            return ip

        except ValueError:
            return "0.0.0.0"

    # ========================================================
    # Submit Lead
    # ========================================================

    def submit(
        self,
        db: Session,
        request,
        payload: SubmissionRequest,
        idempotency_key: str | None
    ):

        # ----------------------------------------------------
        # Validate Widget
        # ----------------------------------------------------

        widget_id = uuid.UUID(payload.widget_id)

        widget = db.get(
            Widget,
            widget_id
        )

        if not widget or not widget.is_active:
            raise HTTPException(
                404,
                "Widget not found"
            )

        # ----------------------------------------------------
        # Honeypot / Spam Protection
        # ----------------------------------------------------

        if payload.honeypot.strip():
            raise HTTPException(
                400,
                "Spam submission rejected"
            )

        # ----------------------------------------------------
        # Idempotency Check
        # ----------------------------------------------------

        if idempotency_key:

            existing = self.repo.get_by_idempotency(
                db,
                widget.id,
                idempotency_key
            )

            if existing:
                return existing, True

        # ----------------------------------------------------
        # Validate Form Fields
        # ----------------------------------------------------

        field_map = {
            f["name"]: f
            for f in widget.fields
        }

        if set(payload.data) - set(field_map):
            raise HTTPException(
                422,
                "Unknown form field"
            )

        for name, field in field_map.items():

            value = payload.data.get(
                name,
                ""
            )

            # Required field validation
            if field.get("required") and not value.strip():
                raise HTTPException(
                    422,
                    f"Field '{name}' is required"
                )

            # Field length validation
            if len(value) > 1000:
                raise HTTPException(
                    422,
                    f"Field '{name}' is too long"
                )

            # Email validation
            if field.get("type") == "email" and value:

                if (
                    "@" not in value
                    or value.startswith("@")
                    or value.endswith("@")
                ):
                    raise HTTPException(
                        422,
                        f"Field '{name}' must be a valid email"
                    )

        # ----------------------------------------------------
        # Geo Location Enrichment
        # ----------------------------------------------------

        geo = self.geo.enrich(
            self.client_ip(request)
        )

        # ----------------------------------------------------
        # Create Submission
        # ----------------------------------------------------

        submission = Submission(
            tenant_id=widget.tenant_id,
            widget_id=widget.id,
            idempotency_key=idempotency_key,
            ip_address=self.client_ip(request),
            country=geo.country,
            city=geo.city,
            geo_provider=geo.provider,
            data=payload.data,
            user_agent=request.headers.get("user-agent")
        )

        db.add(submission)
        db.flush()

        # ----------------------------------------------------
        # Create Background Notification Job
        # ----------------------------------------------------

        job = BackgroundJob(
            submission_id=submission.id,
            job_type="notification",
            payload={
                "submission_id": str(submission.id),
                "widget_id": str(widget.id),
                "tenant_id": str(widget.tenant_id)
            },
            max_attempts=self.settings.max_job_attempts
        )

        db.add(job)

        # ----------------------------------------------------
        # Commit Transaction
        # ----------------------------------------------------

        try:
            db.commit()

        except IntegrityError:

            db.rollback()

            if idempotency_key:

                existing = self.repo.get_by_idempotency(
                    db,
                    widget.id,
                    idempotency_key
                )

                if existing:
                    return existing, True

            raise

        # ----------------------------------------------------
        # Refresh Submission
        # ----------------------------------------------------

        db.refresh(submission)

        return submission, False