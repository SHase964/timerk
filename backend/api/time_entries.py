from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from core.database import SessionDep
from models import TimeEntry
from schemas.time_entry import TimeEntryRead, TimeEntryStartRequest
from services.time_entry import TimeEntryService

router = APIRouter(prefix="/time-entries", tags=["time_entries"])


def get_time_entry_service(session: SessionDep) -> TimeEntryService:
    return TimeEntryService(session)


TimeEntryServiceDep = Annotated[TimeEntryService, Depends(get_time_entry_service)]


@router.get("/active", response_model=TimeEntryRead | None)
def get_active(svc: TimeEntryServiceDep) -> TimeEntry | None:
    return svc.get_active()


@router.post("/start", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
def start_timer(payload: TimeEntryStartRequest, svc: TimeEntryServiceDep) -> TimeEntry:
    try:
        return svc.start(payload.project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/stop", response_model=TimeEntryRead)
def stop_timer(svc: TimeEntryServiceDep) -> TimeEntry:
    entry = svc.stop()
    if entry is None:
        raise HTTPException(status_code=404, detail="No active timer")
    return entry
