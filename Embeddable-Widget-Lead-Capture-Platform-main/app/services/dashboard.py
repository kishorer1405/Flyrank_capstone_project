from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.models.submission import Submission
from app.models.widget import Widget


class DashboardService:

    def stats(self, db, tenant_id):

        # -------------------------------------------------
        # Total Submissions
        # -------------------------------------------------

        total_submissions = db.scalar(
            select(func.count())
            .select_from(Submission)
            .where(
                Submission.tenant_id == tenant_id
            )
        ) or 0


        # -------------------------------------------------
        # Total Widgets
        # -------------------------------------------------

        total_widgets = db.scalar(
            select(func.count())
            .select_from(Widget)
            .where(
                Widget.tenant_id == tenant_id
            )
        ) or 0


        # -------------------------------------------------
        # Submissions By Widget
        # -------------------------------------------------

        by_widget = list(
            db.execute(
                select(
                    Submission.widget_id,
                    func.count().label("count")
                )
                .where(
                    Submission.tenant_id == tenant_id
                )
                .group_by(
                    Submission.widget_id
                )
            )
        )


        # -------------------------------------------------
        # Geographic Breakdown
        # -------------------------------------------------

        geo = list(
            db.execute(
                select(
                    Submission.country,
                    func.count().label("count")
                )
                .where(
                    Submission.tenant_id == tenant_id,
                    Submission.country.is_not(None)
                )
                .group_by(
                    Submission.country
                )
                .order_by(
                    func.count().desc()
                )
            )
        )


        # -------------------------------------------------
        # Last 7 Days
        # -------------------------------------------------

        since = (
            datetime.now(timezone.utc)
            - timedelta(days=7)
        )


        # -------------------------------------------------
        # Daily Submission Statistics
        # -------------------------------------------------

        daily = list(
            db.execute(
                select(
                    func.date(
                        Submission.created_at
                    ).label("day"),

                    func.count().label("count")
                )
                .where(
                    Submission.tenant_id == tenant_id,
                    Submission.created_at >= since
                )
                .group_by(
                    func.date(
                        Submission.created_at
                    )
                )
                .order_by(
                    func.date(
                        Submission.created_at
                    )
                )
            )
        )


        # -------------------------------------------------
        # Return Dashboard Statistics
        # -------------------------------------------------

        return {
            "total_submissions": total_submissions,

            "total_widgets": total_widgets,

            "by_widget": [
                {
                    "widget_id": str(x[0]),
                    "count": x[1]
                }

                for x in by_widget
            ],

            "geo_breakdown": [
                {
                    "country": x[0],
                    "count": x[1]
                }

                for x in geo
            ],

            "submissions_over_time": [
                {
                    "date": str(x[0]),
                    "count": x[1]
                }

                for x in daily
            ]
        }