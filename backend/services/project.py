from sqlmodel import Session, col, select

from backend.models import Project

COLOR_PALETTE = [
    "#FF3B30",
    "#FF9500",
    "#FFCC00",
    "#34C759",
    "#007AFF",
    "#AF52DE",
    "#FF2D55",
    "#5AC8FA",
    "#A2845E",
]


class ProjectService:
    def __init__(self, session: Session):
        self.session = session

    def list_all(self) -> list[Project]:
        statement = select(Project).order_by(col(Project.created_at))
        return list(self.session.exec(statement).all())

    def create(self, name: str, color: str | None = None) -> Project:
        if color is None:
            count = len(self.list_all())
            color = COLOR_PALETTE[count % len(COLOR_PALETTE)]
        project = Project(name=name, color=color)
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        project = self.session.get(Project, project_id)
        if project is None:
            return False
        self.session.delete(project)
        self.session.commit()
        return True

    def update_color(self, project_id: int, color: str) -> Project | None:
        project = self.session.get(Project, project_id)
        if project is None:
            return None
        project.color = color
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
