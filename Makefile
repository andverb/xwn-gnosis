.PHONY: dev migrate migrations db-reset

APP_DIR = app
DB_FILE = app.db

dev:
	uv run fastapi dev app/main.py

migrate:
	uv run alembic upgrade head

migrations:
	@read -p "Migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

db-reset:
	rm -f app.db
	uv run alembic upgrade head
