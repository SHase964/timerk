from sqlmodel import Session, select

from models import Setting


class SettingService:
    def __init__(self, session: Session):
        self.session = session

    def list_all(self) -> list[Setting]:
        return list(self.session.exec(select(Setting)).all())

    def update(self, key: str, value: str) -> Setting | None:
        setting = self.session.get(Setting, key)
        if setting is None:
            return None

        setting.value = value
        self.session.add(setting)
        self.session.commit()
        self.session.refresh(setting)
        return setting
