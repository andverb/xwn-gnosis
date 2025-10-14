"""Admin interface configuration using Starlette Admin."""

from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.exceptions import LoginFailed

from app.config import settings
from app.db import engine
from app.models import Rule, RuleSet


class RuleSetAdmin(ModelView):
    """Admin view for RuleSet model."""

    exclude_fields_from_list = ["rules", "created_at", "updated_at", "created_by", "last_update_by"]
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]
    searchable_fields = ["name", "abbreviation"]
    sortable_fields = ["name", "created_at", "is_official"]
    page_size = 25


class RuleAdmin(ModelView):
    """Admin view for Rule model."""

    exclude_fields_from_list = [
        "translations",
        "meta_data",
        "tags",
        "created_at",
        "updated_at",
        "created_by",
        "last_update_by",
    ]
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]
    searchable_fields = ["type"]
    sortable_fields = ["type", "created_at", "is_official"]
    page_size = 50


class UsernamePasswordProvider(AuthProvider):
    """Simple username/password authentication provider."""

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if username == settings.admin_username and password == settings.admin_password:
            request.session.update({"username": username})
            return response
        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request: Request) -> bool:
        if request.session.get("username") == settings.admin_username:
            request.state.user = settings.admin_username
            return True
        return False

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        return AdminUser(username=user)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response


def create_admin(app) -> Admin:
    """Create and configure admin interface."""
    # Force HTTPS for static files in production
    statics_url = (
        "/admin/statics"
        if settings.environment == "development"
        else "https://xwn-gnosis-production.up.railway.app/admin/statics"
    )

    admin = Admin(
        engine,
        title="Gnosis Admin",
        base_url="/admin",
        statics_url=statics_url,
        auth_provider=UsernamePasswordProvider(),
    )

    # Add model views
    admin.add_view(RuleSetAdmin(RuleSet, icon="fa fa-book"))
    admin.add_view(RuleAdmin(Rule, icon="fa fa-file-text"))

    # Mount admin to app
    admin.mount_to(app)

    return admin
