# xWN Gnosis

[![Tests](https://github.com/andverb/xwn-gnosis/actions/workflows/tests.yml/badge.svg)](https://github.com/andverb/xwn-gnosis/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/andverb/xwn-gnosis/branch/main/graph/badge.svg)](https://codecov.io/gh/andverb/xwn-gnosis)

This is a rules database for xWN family of tabletop roleplaying games.

Features planned: 
1. Fuzzy search the rules in SRD
2. REST API with openAPI docs (public part is read-only)
3. Tags system for rules
4. Rules have interlinking
5. ENG and UK interface 
6. ENG and UK rules content
7. Ability to tag system
8. Ability to add homebrew rules
9. Different rulesets support

Features expanded:
1. Tools to roll on random tables from SRD, like tags system, court generation, etc
2. Monsters database, with search and ability to pick weapon
3. Weapons, cyber, spells, etc. - search and tables
4. Encounter builder with guidelines
5. Monster builder with powers from SRD
6. Dungeon generator and stocking
7. Dungeon turns tracker
8. Hex crawl generator
9. Mission generator

## Technical Stack

### Backend
- [FastAPI](https://fastapi.tiangolo.com/) - ASGI web framework
- [PostgreSQL](https://www.postgresql.org/) - Production database with async support
- [SQLAlchemy](https://www.sqlalchemy.org/) - Async ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management
- [Granian](https://github.com/emmett-framework/granian) - Rust-based ASGI server for production

### Frontend
- [htmx](https://htmx.org/) - Dynamic HTML interactions without JavaScript
- [Jinja2](https://jinja.palletsprojects.com/) - Server-side template engine
- [Pico CSS](https://picocss.com/) - Minimal CSS framework with dark/light themes
- [Python-Markdown](https://python-markdown.github.io/) - Markdown to HTML conversion
- [Bleach](https://bleach.readthedocs.io/) - HTML sanitization

### Admin Interface
- [Starlette Admin](https://github.com/jowilf/starlette-admin) - Full-featured admin panel with authentication
- [EasyMDE](https://github.com/Ionaru/easy-markdown-editor) - Markdown editor for content management

### Infrastructure
- [Docker](https://www.docker.com/) + [Docker Compose](https://docs.docker.com/compose/) - Containerization
- Deployed on [Railway](https://railway.app/) - https://xwn-gnosis-production.up.railway.app
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### Testing & CI/CD
- [pytest](https://docs.pytest.org/) - Testing framework with async support
- [pytest-cov](https://pytest-cov.readthedocs.io/) - Code coverage reporting
- GitHub Actions - Automated testing and coverage reports
- [Codecov](https://codecov.io/) - Code coverage tracking and badges

### Planned/Future
- [FastAPI Users](https://github.com/fastapi-users/fastapi-users) - User authentication system