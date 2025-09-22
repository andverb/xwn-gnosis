from datetime import datetime

from pydantic import BaseModel, ConfigDict

# Follow the pattern - User data in Base, requirements in Create, database data in Response.


class RuleContent(BaseModel):
    # Internal structure of multi-language rule description
    name: str
    description: str


class RuleBase(BaseModel):
    # Fields that are SHARED between create/response
    tags: list[str] | None = None
    # Dict with multiple language versions of the rule
    translations: dict[str, RuleContent]
    changes_description: str | None = None
    is_official: bool = False


class RuleCreate(RuleBase):
    # Inherits shared fields + any create-specific fields
    ruleset_id: int
    base_rule_id: int | None = None


class RuleUpdate(BaseModel):
    # Inherits from BaseModel, not from RuleBase so all fields optional for partial updates
    tags: list[str] | None = None
    translations: dict[str, RuleContent] | None = None
    changes_description: str | None = None
    is_official: bool = False


class Rule(RuleBase):
    # Response validation - inherits shared fields + database-generated fields
    model_config = ConfigDict(from_attributes=True)

    id: int
    ruleset_id: int
    base_rule_id: int | None = None
    slug: str

    created_at: datetime
    updated_at: datetime

    # TODO add users and relations
    created_by: str | None = None
    last_update_by: str | None = None

    def get_content(self, lang: str = "en") -> RuleContent:
        """Get content for specific language, fallback to English"""
        content = self.translations.get(lang, self.translations.get("en"))
        if content is None:
            raise ValueError(f"No content available for language: {lang}")
        return RuleContent(**content) if isinstance(content, dict) else content


class RuleSetBase(BaseModel):
    name: str
    description: str | None = None


class RuleSetCreate(RuleSetBase):
    base_ruleset_id: int | None = None


class RuleSetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RuleSet(RuleSetBase):
    # Response model
    model_config = ConfigDict(from_attributes=True)

    id: int
    base_ruleset_id: int | None = None
    slug: str
    created_at: datetime
    updated_at: datetime
    # TODO consider making those non-nullable since we will auto-populate those as admin
    created_by: str | None = None
    last_update_by: str | None = None
