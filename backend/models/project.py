from datetime import datetime

from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    color: str = Field(default="blue")
    created_at: datetime = Field(default_factory=datetime.now)
