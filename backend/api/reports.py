from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.core.database import SessionDep
from backend.schemas.report import ReportSummary
from backend.services.report import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service(session: SessionDep) -> ReportService:
    return ReportService(session)


ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]


@router.get("", response_model=ReportSummary)
def report_summary(
    svc: ReportServiceDep,
    date_from: Annotated[date, Query(alias="from")],
    date_to: Annotated[date, Query(alias="to")],
) -> ReportSummary:
    return svc.summary(date_from, date_to)
