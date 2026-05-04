.PHONY: lint
lint:
	uv run ruff format backend
	uv run ruff check --fix backend
	uv run mypy backend --explicit-package-bases