from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.database import get_session
from schemas.project import ProjectCreate, ProjectRead
from services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(session: Session = Depends(get_session)) -> ProjectService:
    return ProjectService(session)


@router.get("", response_model=list[ProjectRead])
def list_projects(svc: ProjectService = Depends(get_project_service)):
    return svc.list_all()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    svc: ProjectService = Depends(get_project_service),
):
    return svc.create(payload.name)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    svc: ProjectService = Depends(get_project_service),
):
    if not svc.delete(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
