from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from core.database import get_session
from schemas.time_entry import TimeEntryRead, TimeEntryStartRequest
from services.time_entry import TimeEntryService

router = APIRouter(prefix="/time-entries", tags=["time_entries"])


def get_time_entry_service(
    session: Session = Depends(get_session),
) -> TimeEntryService:
    return TimeEntryService(session)


@router.get("/active", response_model=TimeEntryRead | None)
def get_active(svc: TimeEntryService = Depends(get_time_entry_service)):
    return svc.get_active()


@router.post(
    "/start", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED
)
def start_timer(
    payload: TimeEntryStartRequest,
    svc: TimeEntryService = Depends(get_time_entry_service),
):
    try:
        return svc.start(payload.project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stop", response_model=TimeEntryRead)
def stop_timer(svc: TimeEntryService = Depends(get_time_entry_service)):
    entry = svc.stop()
    if entry is None:
        raise HTTPException(status_code=404, detail="No active timer")
    return entry
