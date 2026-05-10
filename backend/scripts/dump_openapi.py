from pathlib import Path

import yaml  # type: ignore[import-untyped]

from backend.main import app

OUTPUT = Path(__file__).resolve().parent.parent / "openapi.yml"


def main() -> None:
    schema = app.openapi()
    OUTPUT.write_text(
        yaml.safe_dump(schema, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
