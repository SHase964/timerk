.PHONY: lint
lint: lint-backend lint-frontend

.PHONY: lint-backend
lint-backend:
	uv run ruff format backend
	uv run ruff check --fix backend
	uv run mypy backend menubar main_app.py --explicit-package-bases

.PHONY: lint-frontend
lint-frontend:
	cd frontend && npm run lint -- --fix

.PHONY: oapigen
oapigen:
	uv run python -m backend.scripts.dump_openapi

.PHONY: frontend-build
frontend-build:
	cd frontend && npm run build

.PHONY: app
app: frontend-build
	rm -rf build dist
	uv run python setup.py py2app -A

.PHONY: app-release
app-release: frontend-build
	rm -rf build dist
	uv run python setup.py py2app
