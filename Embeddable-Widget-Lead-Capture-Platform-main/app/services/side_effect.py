import logging

from app.core.config import Settings


logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self, settings: Settings):
        self.s = settings

    def send(self, payload: dict) -> None:

        if self.s.side_effect_fail:
            raise RuntimeError(
                "Deterministic side-effect failure enabled"
            )

        if self.s.side_effect_mode == "console":
            logger.info(
                "Notification side effect queued for submission_id=%s",
                payload.get("submission_id")
            )

        else:
            logger.info(
                "Notification side effect completed for submission_id=%s",
                payload.get("submission_id")
            )