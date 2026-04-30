from sqlmodel import SQLModel


class SettingRead(SQLModel):
    key: str
    value: str


class SettingUpdate(SQLModel):
    value: str
