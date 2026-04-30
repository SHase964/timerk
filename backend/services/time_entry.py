from datetime import datetime

from sqlmodel import Session, col, select

from models import Project, TimeEntry


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

    def _close_entry(self, entry: TimeEntry, stopped_at: datetime) -> None:
        entry.stopped_at = stopped_at
        entry.duration_sec = int((stopped_at - entry.started_at).total_seconds())
        self.session.add(entry)
