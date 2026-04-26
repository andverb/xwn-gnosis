.PHONY: run migrate migrations static index lint test build shell

run:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate

migrations:
	uv run python manage.py makemigrations

static:
	uv run python manage.py collectstatic --noinput

index:
	uv run python manage.py build_content_index

index-en:
	uv run python manage.py build_content_index --lang en

index-uk:
	uv run python manage.py build_content_index --lang uk

lint:
	uv run ruff check --fix && uv run ruff format

test:
	uv run pytest

shell:
	uv run python manage.py shell

# Full local setup after clone / pulling new deps
setup:
	uv sync
	uv run python manage.py migrate
	uv run python manage.py build_content_index
