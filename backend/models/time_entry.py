from datetime import datetime

from sqlmodel import Field, SQLModel


class TimeEntry(SQLModel, table=True):
    __tablename__ = "time_entries"

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    started_at: datetime
    stopped_at: datetime | None = None
    duration_sec: int | None = None
