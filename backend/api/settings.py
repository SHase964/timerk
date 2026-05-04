from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from core.database import SessionDep
from models import Setting
from schemas.setting import SettingRead, SettingUpdate
from services.setting import SettingService

router = APIRouter(prefix="/settings", tags=["settings"])


def get_setting_service(session: SessionDep) -> SettingService:
    return SettingService(session)


SettingServiceDep = Annotated[SettingService, Depends(get_setting_service)]


@router.get("", response_model=list[SettingRead])
def list_settings(svc: SettingServiceDep) -> list[Setting]:
    return svc.list_all()


@router.put("/{key}", response_model=SettingRead)
def update_setting(key: str, payload: SettingUpdate, svc: SettingServiceDep) -> Setting:
    setting = svc.update(key, payload.value)
    if setting is None:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return setting
