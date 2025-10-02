.PHONY: dev dev-docker migrate migrations db-reset backup

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

backup:
	@mkdir -p backups
	docker exec xwn-gnosis-postgres-1 pg_dump -U gnosis_user gnosis_db > backups/db_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup created in backups/ directory"
