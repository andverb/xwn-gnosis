from crudadmin import CRUDAdmin

from app import models, schemas
from app.config import settings
from app.db import get_db

admin = CRUDAdmin(
    session=get_db,
    session_backend="memory",  # Use in-memory sessions (simple, no DB writes)
    SECRET_KEY=settings.secret_key,
    initial_admin={
        "username": "sorcererkingadmin",  # No underscores allowed
        "password": settings.admin_password,
    },
)

admin.add_view(
    model=models.Rule,
    create_schema=schemas.RuleCreate,
    update_schema=schemas.RuleUpdate,
    allowed_actions={"view", "create", "update", "delete"},
)

admin.add_view(
    model=models.RuleSet,
    create_schema=schemas.RuleSetCreate,
    update_schema=schemas.RuleSetUpdate,
    allowed_actions={"view", "create", "update", "delete"},
)
