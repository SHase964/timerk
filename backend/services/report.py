from datetime import date

from sqlalchemy import func
from sqlmodel import Session, col, select

from backend.models import Project, TimeEntry
from backend.schemas.report import DailyPoint, ProjectBreakdown, ReportSummary


class ReportService:
    def __init__(self, session: Session):
        self.session = session

    def summary(self, date_from: date, date_to: date) -> ReportSummary:
        from_str = date_from.isoformat()
        to_str = date_to.isoformat()
        date_expr = func.date(TimeEntry.started_at)

        daily_stmt = (
            select(
                date_expr.label("date"),
                func.coalesce(func.sum(TimeEntry.duration_sec), 0).label("total_sec"),
            )
            .where(col(TimeEntry.stopped_at).is_not(None))
            .where(date_expr >= from_str)
            .where(date_expr <= to_str)
            .group_by(date_expr)
            .order_by(date_expr.asc())
        )
        daily_rows = self.session.exec(daily_stmt).all()
        daily = [DailyPoint(date=r.date, total_sec=int(r.total_sec)) for r in daily_rows]

        project_stmt = (
            select(
                Project.id,
                Project.name,
                Project.color,
                func.coalesce(func.sum(TimeEntry.duration_sec), 0).label("total_sec"),
            )
            .join(
                TimeEntry,
                (TimeEntry.project_id == Project.id)
                & col(TimeEntry.stopped_at).is_not(None)
                & (date_expr >= from_str)
                & (date_expr <= to_str),
                isouter=True,
            )
            .group_by(Project.id, Project.name, Project.color)
            .order_by(func.coalesce(func.sum(TimeEntry.duration_sec), 0).desc())
        )
        project_rows = self.session.exec(project_stmt).all()
        by_project = [
            ProjectBreakdown(
                project_id=r.id,
                name=r.name,
                color=r.color,
                total_sec=int(r.total_sec),
            )
            for r in project_rows
        ]

        total_sec = sum(d.total_sec for d in daily)

        return ReportSummary(
            date_from=from_str,
            date_to=to_str,
            total_sec=total_sec,
            daily=daily,
            by_project=by_project,
        )
