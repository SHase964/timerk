from sqlmodel import SQLModel


class DailyPoint(SQLModel):
    date: str  # "2026-04-23"
    total_sec: int


class ProjectBreakdown(SQLModel):
    project_id: int
    name: str
    color: str
    total_sec: int


class ReportSummary(SQLModel):
    date_from: str
    date_to: str
    total_sec: int
    daily: list[DailyPoint]
    by_project: list[ProjectBreakdown]
