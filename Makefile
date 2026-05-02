.PHONY: run migrate migrations static index lint test test-js build shell

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

test-js:
	node --test tests/faction-tracker/rules.test.js tests/faction-tracker/storage.test.js

shell:
	uv run python manage.py shell

# Full local setup after clone / pulling new deps
setup:
	uv sync
	uv run python manage.py migrate
	uv run python manage.py build_content_index
