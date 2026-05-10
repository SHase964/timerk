.PHONY: lint
lint: lint-backend lint-frontend

.PHONY: lint-backend
lint-backend:
	uv run ruff format backend
	uv run ruff check --fix backend
	uv run mypy backend --explicit-package-bases

.PHONY: lint-frontend
lint-frontend:
	cd frontend && npm run lint -- --fix

.PHONY: oapigen
oapigen:
	uv run python -m backend.scripts.dump_openapi
