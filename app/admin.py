"""Admin interface configuration using Starlette Admin."""

import urllib.parse

from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.contrib.sqla import Admin
from starlette_admin.contrib.sqla.ext.pydantic import ModelView
from starlette_admin.exceptions import LoginFailed
from starlette_admin.fields import TextAreaField

from app.config import settings
from app.db import engine
from app.models import Rule, RuleSet
from app.schemas import RuleCreate, RuleSetCreate


class MarkdownField(TextAreaField):
    """Custom field for markdown editing with EasyMDE.

    This field extends TextAreaField to provide a rich markdown editing experience
    using the EasyMDE editor. The editor is automatically initialized via JavaScript
    included in additional_js_links.
    """

    def additional_css_links(self, request: Request, action) -> list[str]:
        """Include EasyMDE CSS in the page head."""
        return [
            "https://cdn.jsdelivr.net/npm/easymde@2.18.0/dist/easymde.min.css",
        ]

    def additional_js_links(self, request: Request, action) -> list[str]:
        """Include EasyMDE JS library and initialization script."""
        links = [
            "https://cdn.jsdelivr.net/npm/easymde@2.18.0/dist/easymde.min.js",
        ]

        # TODO: Find a better way of doing this using documented approaches:
        # 1. Custom form template: https://jowilf.github.io/starlette-admin/advanced/custom-field/
        # 2. Custom render JS: https://jowilf.github.io/starlette-admin/advanced/custom-field/#custom-render-js
        # 3. EasyMDE usage: https://github.com/Ionaru/easy-markdown-editor#usage
        # Current approach uses data URL as a workaround since custom templates had resolution issues
        init_script = """
        (function() {
            function initEditors() {
                if (typeof EasyMDE === 'undefined') {
                    setTimeout(initEditors, 100);
                    return;
                }
                var textareas = document.querySelectorAll('textarea[name="description"],
                 textarea[name="description_en"], textarea[name="description_uk"],
                  textarea[name="changes_description"]');
                textareas.forEach(function(textarea) {
                    try {
                        new EasyMDE({
                            element: textarea,
                            spellChecker: false,
                            toolbar: ["table", "bold", "italic", "heading", "|",
                             "quote", "unordered-list", "ordered-list", "link", "|",
                              "preview", "side-by-side", "fullscreen", "|", "guide"],
                            status: ["lines", "words", "cursor"],
                            placeholder: "Enter description in Markdown format...",
                            minHeight: "300px",
                            lineWrapping: true,
                            sideBySideFullscreen: false,
                        });
                    } catch (e) {
                        console.error('EasyMDE initialization error:', e);
                    }
                });
            }
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initEditors);
            } else {
                initEditors();
            }
        })();
        """
        # URL-encode the script
        encoded = urllib.parse.quote(init_script)
        links.append(f"data:text/javascript,{encoded}")

        return links


class RuleSetAdmin(ModelView):
    """Admin view for RuleSet model."""

    exclude_fields_from_list = ["rules", "created_at", "updated_at", "created_by", "last_update_by"]
    exclude_fields_from_create = ["created_at", "updated_at"]
    exclude_fields_from_edit = ["created_at", "updated_at"]
    searchable_fields = ["name", "abbreviation"]
    sortable_fields = ["name", "created_at", "is_official"]
    page_size = 25

    # Configure custom fields with EasyMDE for markdown editing
    fields = [
        "id",
        "name",
        "slug",
        "abbreviation",
        MarkdownField("description", label="Description"),
        "is_official",
        "base_ruleset_id",
        "rules",
        "created_at",
        "updated_at",
        "created_by",
        "last_update_by",
    ]


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

    # Configure custom fields with EasyMDE for markdown editing
    fields = [
        "id",
        "type",
        "tags",
        "meta_data",
        "name_en",
        MarkdownField("description_en", label="Description (EN)"),
        "name_uk",
        MarkdownField("description_uk", label="Description (UK)"),
        "slug",
        MarkdownField("changes_description", label="Changes Description"),
        "is_official",
        "ruleset_id",
        "base_rule_id",
        "created_at",
        "updated_at",
        "created_by",
        "last_update_by",
    ]


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
    """Create and configure admin interface with EasyMDE support."""
    admin = Admin(
        engine,
        title="Gnosis Admin",
        base_url="/admin",
        auth_provider=UsernamePasswordProvider(),
    )

    # Add model views with Pydantic validation
    admin.add_view(RuleSetAdmin(RuleSet, icon="fa fa-book", pydantic_model=RuleSetCreate))
    admin.add_view(RuleAdmin(Rule, icon="fa fa-file-text", pydantic_model=RuleCreate))

    # Mount admin to app
    admin.mount_to(app)

    return admin
