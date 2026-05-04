from datetime import datetime

from sqlmodel import SQLModel


class ProjectCreate(SQLModel):
    name: str
    color: str | None = None


class ProjectUpdate(SQLModel):
    color: str


class ProjectRead(SQLModel):
    id: int
    name: str
    color: str
    created_at: datetime
