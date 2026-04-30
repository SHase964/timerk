from sqlmodel import Session, select

from models import Project


class ProjectService:
    def __init__(self, session: Session):
        self.session = session

    def list_all(self) -> list[Project]:
        statement = select(Project).order_by(Project.created_at)
        return list(self.session.exec(statement).all())

    def create(self, name: str) -> Project:
        project = Project(name=name)
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
