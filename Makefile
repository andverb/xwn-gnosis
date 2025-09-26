.PHONY: dev dev-docker migrate migrations db-reset

APP_DIR = app
DB_FILE = app.db

dev:
	uv run fastapi dev app/main.py

dev-docker:
	docker-compose up --build

migrate:
	uv run alembic upgrade head

migrations:
	@read -p "Migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

db-reset:
	rm -f app.db
	uv run alembic upgrade head
