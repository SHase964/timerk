from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.core.database import SessionDep
from backend.models import TimeEntry
from backend.schemas.time_entry import TimeEntryRead, TimeEntryStartRequest, TimeEntryUpdateRequest
from backend.services.time_entry import TimeEntryService

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


@router.get("", response_model=list[TimeEntryRead])
def list_time_entries(
    svc: TimeEntryServiceDep,
    date_from: Annotated[date, Query(alias="from")],
    date_to: Annotated[date, Query(alias="to")],
) -> list[TimeEntry]:
    return svc.list_entries(date_from, date_to)


@router.patch("/{entry_id}", response_model=TimeEntryRead)
def update_entry(
    entry_id: int,
    payload: TimeEntryUpdateRequest,
    svc: TimeEntryServiceDep,
) -> TimeEntry:
    try:
        entry = svc.update(entry_id, payload.started_at, payload.stopped_at)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, svc: TimeEntryServiceDep) -> None:
    try:
        svc.delete(entry_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Time entry not found") from None
