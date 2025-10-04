.PHONY: dev dev-docker migrate migrations db-reset backup generate-secrets

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

generate-secrets:
	@echo "=== Gnosis Production Secrets ==="
	@echo ""
	@echo "API Key (for write operations):"
	@python3 -c "import secrets; print('GNOSIS_API_KEY=' + secrets.token_urlsafe(32))"
	@echo ""
	@echo "Database Password (24 characters):"
	@python3 -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(24))"
	@echo ""
	@echo "=== IMPORTANT ==="
	@echo "1. Save these secrets securely (password manager)"
	@echo "2. Never commit these to git"
	@echo "3. Set them in your production environment"
	@echo "4. Use different secrets for dev/staging/prod"