.PHONY: dev dev-docker migrate migrations db-reset backup generate-secrets dump-data restore-data build-rulesets

include .env
export

APP_DIR = app
DB_FILE = app.db
# Convert asyncpg URL to postgresql URL for pg_dump/psql
DB_URL = $(shell echo $(DATABASE_URL) | sed 's/postgresql+asyncpg/postgresql/')

dev:
	uv run fastapi dev app/main.py

dev-docker:
	docker-compose up --build

build-rulesets:
	@echo "Building Ukrainian documentation..."
	uv run mkdocs build -f mkdocs-uk.yml --clean
	@echo "Building English documentation..."
	uv run mkdocs build -f mkdocs-en.yml --clean
	@echo "✅ Rulesets built successfully!"

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

# Export local database data
dump-data:
	@mkdir -p data/dumps
	@echo "Dumping local database data..."
	@docker exec xwn-gnosis-postgres-1 pg_dump -U gnosis_user gnosis_db \
		--data-only --table=rulesets --table=rules --column-inserts \
		> data/dumps/gnosis_data_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Data dump created in data/dumps/"

# Import data into local database
restore-data:
	@mkdir -p data/dumps
	@echo "Available dumps:"
	@ls -1t data/dumps/*.sql 2>/dev/null | head -10 || echo "No dumps found"
	@echo ""
	@read -p "Enter dump filename: " file; \
	if [ ! -f "$$file" ]; then \
		echo "File not found: $$file"; \
		exit 1; \
	fi; \
	psql "$(DB_URL)" -f "$$file" && \
	echo "Data restored from $$file"