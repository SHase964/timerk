from datetime import datetime

from sqlmodel import SQLModel


class ProjectCreate(SQLModel):
    name: str


class ProjectRead(SQLModel):
    id: int
    name: str
    created_at: datetime
