from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from core.database import SessionDep
from models import Project
from schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(session: SessionDep) -> ProjectService:
    return ProjectService(session)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]


@router.get("", response_model=list[ProjectRead])
def list_projects(svc: ProjectServiceDep) -> list[Project]:
    return svc.list_all()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, svc: ProjectServiceDep) -> Project:
    return svc.create(payload.name, payload.color)


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, payload: ProjectUpdate, svc: ProjectServiceDep) -> Project:
    project = svc.update_color(project_id, payload.color)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, svc: ProjectServiceDep) -> None:
    if not svc.delete(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
