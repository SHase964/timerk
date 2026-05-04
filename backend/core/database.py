from collections.abc import Generator
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import event, text
from sqlmodel import Session, SQLModel, create_engine, select

from backend.models import Setting

PALETTE = [
    "#FF3B30",
    "#FF9500",
    "#FFCC00",
    "#34C759",
    "#007AFF",
    "#AF52DE",
    "#FF2D55",
    "#5AC8FA",
    "#A2845E",
]

NAME_TO_HEX = {
    "red": "#FF3B30",
    "orange": "#FF9500",
    "yellow": "#FFCC00",
    "green": "#34C759",
    "blue": "#007AFF",
    "purple": "#AF52DE",
    "brown": "#A2845E",
    "black": "#000000",
    "white": "#FFFFFF",
}

DB_PATH = Path.home() / "timerk" / "timerk.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_conn: Any, _: Any) -> None:
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    _migrate_add_color_column()
    _migrate_palette_names_to_hex()

    with Session(engine) as session:
        existing = session.exec(select(Setting).where(Setting.key == "show_seconds")).first()
        if existing is None:
            session.add(Setting(key="show_seconds", value="false"))
            session.commit()


def _migrate_add_color_column() -> None:
    with engine.begin() as conn:
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(projects)"))]
        if "color" in cols:
            return
        conn.execute(text("ALTER TABLE projects ADD COLUMN color TEXT NOT NULL DEFAULT '#007AFF'"))
        rows = conn.execute(text("SELECT id FROM projects ORDER BY id")).all()
        for i, (pid,) in enumerate(rows):
            conn.execute(
                text("UPDATE projects SET color = :c WHERE id = :id"),
                {"c": PALETTE[i % len(PALETTE)], "id": pid},
            )


def _migrate_palette_names_to_hex() -> None:
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT id, color FROM projects")).all()
        for pid, color in rows:
            if color in NAME_TO_HEX:
                conn.execute(
                    text("UPDATE projects SET color = :c WHERE id = :id"),
                    {"c": NAME_TO_HEX[color], "id": pid},
                )


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


if __name__ == "__main__":
    init_db()
    print(f"Initialized DB at {DB_PATH}")
