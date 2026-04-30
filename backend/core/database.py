from collections.abc import Generator
from pathlib import Path

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine, select

import models  # noqa: F401  # SQLModel.metadata にテーブル登録するための副作用 import
from models import Setting

DB_PATH = Path.home() / "timerk" / "timerk.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.exec(
            select(Setting).where(Setting.key == "timer_unit")
        ).first()
        if existing is None:
            session.add(Setting(key="timer_unit", value="min"))
            session.commit()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    init_db()
    print(f"Initialized DB at {DB_PATH}")
