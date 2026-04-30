from datetime import datetime

from sqlmodel import SQLModel


class TimeEntryStartRequest(SQLModel):
    project_id: int


class TimeEntryRead(SQLModel):
    id: int
    project_id: int
    started_at: datetime
    stopped_at: datetime | None = None
    duration_sec: int | None = None
