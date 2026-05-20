from datetime import date, datetime

from sqlalchemy import func
from sqlmodel import Session, col, select

from backend.models import Project, TimeEntry


class TimeEntryService:
    def __init__(self, session: Session):
        self.session = session

    def get_active(self) -> TimeEntry | None:
        statement = select(TimeEntry).where(col(TimeEntry.stopped_at).is_(None))
        return self.session.exec(statement).first()

    def start(self, project_id: int) -> TimeEntry:
        project = self.session.get(Project, project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")

        now = datetime.now()

        active = self.get_active()
        if active is not None:
            self._close_entry(active, now)

        new_entry = TimeEntry(project_id=project_id, started_at=now)
        self.session.add(new_entry)
        self.session.commit()
        self.session.refresh(new_entry)
        return new_entry

    def stop(self) -> TimeEntry | None:
        active = self.get_active()
        if active is None:
            return None

        self._close_entry(active, datetime.now())
        self.session.commit()
        self.session.refresh(active)
        return active

    def list_entries(self, date_from: date, date_to: date) -> list[TimeEntry]:
        """started_at の日付が [date_from, date_to] に入るエントリを時系列で返す。"""
        date_expr = func.date(TimeEntry.started_at)
        statement = (
            select(TimeEntry)
            .where(date_expr >= date_from.isoformat())
            .where(date_expr <= date_to.isoformat())
            .order_by(col(TimeEntry.started_at).asc())
        )
        return list(self.session.exec(statement).all())

    def update(
        self,
        entry_id: int,
        started_at: datetime | None,
        stopped_at: datetime | None,
    ) -> TimeEntry | None:
        entry = self.session.get(TimeEntry, entry_id)
        if entry is None:
            return None

        # None のフィールドは「変更なし」とみなして既存値を使う
        new_started = started_at if started_at is not None else entry.started_at
        new_stopped = stopped_at if stopped_at is not None else entry.stopped_at

        if new_stopped is not None and new_started >= new_stopped:
            raise ValueError("started_at must be before stopped_at")

        entry.started_at = new_started
        entry.stopped_at = new_stopped
        if new_stopped is not None:
            entry.duration_sec = int((new_stopped - new_started).total_seconds())
        else:
            entry.duration_sec = None

        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def delete(self, entry_id: int) -> None:
        entry = self.session.get(TimeEntry, entry_id)
        if entry is None:
            raise ValueError(f"TimeEntry {entry_id} not found")

        self.session.delete(entry)
        self.session.commit()

    def _close_entry(self, entry: TimeEntry, stopped_at: datetime) -> None:
        entry.stopped_at = stopped_at
        entry.duration_sec = int((stopped_at - entry.started_at).total_seconds())
        self.session.add(entry)
