from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.database import get_session
from schemas.setting import SettingRead, SettingUpdate
from services.setting import SettingService

router = APIRouter(prefix="/settings", tags=["settings"])


def get_setting_service(session: Session = Depends(get_session)) -> SettingService:
    return SettingService(session)


@router.get("", response_model=list[SettingRead])
def list_settings(svc: SettingService = Depends(get_setting_service)):
    return svc.list_all()


@router.put("/{key}", response_model=SettingRead)
def update_setting(
    key: str,
    payload: SettingUpdate,
    svc: SettingService = Depends(get_setting_service),
):
    setting = svc.update(key, payload.value)
    if setting is None:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return setting
