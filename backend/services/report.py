from collections import defaultdict
from datetime import date

from sqlalchemy import func
from sqlmodel import Session, col, select

from backend.models import Project, TimeEntry
from backend.schemas.report import (
    DailyPoint,
    DailyProjectPoint,
    ProjectBreakdown,
    ReportSummary,
)


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
                TimeEntry.project_id,
                func.coalesce(func.sum(TimeEntry.duration_sec), 0).label("total_sec"),
            )
            .where(col(TimeEntry.stopped_at).is_not(None))
            .where(date_expr >= from_str)
            .where(date_expr <= to_str)
            .group_by(date_expr, TimeEntry.project_id)
            .order_by(date_expr.asc(), col(TimeEntry.project_id).asc())
        )
        daily_rows = self.session.exec(daily_stmt).all()
        by_date: dict[str, list[DailyProjectPoint]] = defaultdict(list)
        for r in daily_rows:
            by_date[r.date].append(
                DailyProjectPoint(project_id=r.project_id, total_sec=int(r.total_sec))
            )
        daily = [
            DailyPoint(
                date=d,
                total_sec=sum(p.total_sec for p in by_date[d]),
                by_project=by_date[d],
            )
            for d in sorted(by_date.keys())
        ]

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
