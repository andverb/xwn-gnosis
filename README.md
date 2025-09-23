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

### Current
- [FastAPI](https://fastapi.tiangolo.com/) - ASGI web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Pydantic](https://docs.pydantic.dev/) - Data validation

### Planned
**Frontend:**
- [htmx](https://htmx.org/) - Dynamic HTML interactions
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [Alpine.js](https://alpinejs.dev/) - Lightweight JS framework
- CSS: [Simple.css](https://simplecss.org/) or [Beer CSS](https://www.beercss.com/)
- [Tabler](https://tabler.io/) - Admin template

**Backend:**
- [FastHX](https://volfpeter.github.io/fasthx/) - FastAPI + htmx integration
- [FastAPI Users](https://github.com/fastapi-users/fastapi-users) - Authentication
- [Structlog](https://www.structlog.org/) - Structured logging
- PostgreSQL with fuzzy search

**Admin Interface:**
- [Starlette Admin](https://github.com/jowilf/starlette-admin) - Generic admin interface
- [SQLAdmin](https://github.com/aminalaee/sqladmin) - SQLAlchemy-focused admin panel

**Infrastructure:**
- Docker + Docker Compose for local development
- Deployment on render.com or railway.com
- GitHub Actions CI/CD