from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Follow the pattern - User data in Base, requirements in Create, database data in Response.


class RuleBase(BaseModel):
    # Fields that are SHARED between create/response
    type: str | None = Field(default=None, max_length=50)
    tags: list[str] | None = None
    meta_data: dict | None = None

    # Separate fields for each language
    name_en: str = Field(min_length=1, max_length=200)
    description_en: str = Field(min_length=1)
    name_uk: str | None = Field(default=None, max_length=200)
    description_uk: str | None = None

    changes_description: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str | None) -> str | None:
        """Validate rule type against known types."""
        if v is None:
            return v

        valid_types = {
            "rule",
            "skill",
            "background",
            "class",
            "focus",
            "art",
            "spell",
            "weapon",
            "armor",
            "combat-action",
            "faction",
            "downtime",
        }

        if v not in valid_types:
            raise ValueError(f"Invalid rule type '{v}'. Must be one of: {', '.join(sorted(valid_types))}")
        return v

    @field_validator("name_en")
    @classmethod
    def name_en_not_empty(cls, v: str) -> str:
        """Ensure English name is not just whitespace."""
        if not v.strip():
            raise ValueError("English name cannot be empty or just whitespace")
        return v.strip()

    @field_validator("description_en")
    @classmethod
    def description_en_not_empty(cls, v: str) -> str:
        """Ensure English description is not just whitespace."""
        if not v.strip():
            raise ValueError("English description cannot be empty or just whitespace")
        return v.strip()

    @field_validator("name_uk")
    @classmethod
    def name_uk_not_empty(cls, v: str | None) -> str | None:
        """Ensure Ukrainian name is not just whitespace if provided."""
        if v and not v.strip():
            raise ValueError("Ukrainian name cannot be just whitespace")
        return v.strip() if v else None

    @field_validator("description_uk")
    @classmethod
    def description_uk_not_empty(cls, v: str | None) -> str | None:
        """Ensure Ukrainian description is not just whitespace if provided."""
        if v and not v.strip():
            raise ValueError("Ukrainian description cannot be just whitespace")
        return v.strip() if v else None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Ensure tags are non-empty strings."""
        if v is None:
            return v

        if not all(isinstance(tag, str) and tag.strip() for tag in v):
            raise ValueError("All tags must be non-empty strings")

        # Remove duplicates and sort
        return sorted({tag.strip().lower() for tag in v})


class RuleCreate(RuleBase):
    # Inherits shared fields + any create-specific fields
    ruleset_id: int
    base_rule_id: int | None = None


class RuleUpdate(BaseModel):
    # Inherits from BaseModel, not from RuleBase so all fields optional for partial updates
    type: str | None = None
    tags: list[str] | None = None
    meta_data: dict | None = None
    name_en: str | None = None
    description_en: str | None = None
    name_uk: str | None = None
    description_uk: str | None = None
    changes_description: str | None = None
    # Note: is_official is NOT editable here - it's synced from ruleset


class Rule(RuleBase):
    # Response validation - inherits shared fields + database-generated fields
    model_config = ConfigDict(from_attributes=True)

    id: int
    ruleset_id: int
    base_rule_id: int | None = None
    slug: str
    is_official: bool  # Read-only: synced from ruleset

    created_at: datetime
    updated_at: datetime

    # TODO add users and relations
    created_by: str | None = None
    last_update_by: str | None = None

    def get_name(self, lang: str = "en") -> str:
        """Get rule name in specified language, fallback to English"""
        if lang == "uk" and self.name_uk:
            return self.name_uk
        return self.name_en

    def get_description(self, lang: str = "en") -> str:
        """Get rule description in specified language, fallback to English"""
        if lang == "uk" and self.description_uk:
            return self.description_uk
        return self.description_en


class RuleSetBase(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    abbreviation: str | None = Field(default=None, max_length=20)
    description: str | None = None
    is_official: bool = False

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()


class RuleSetCreate(RuleSetBase):
    base_ruleset_id: int | None = None


class RuleSetUpdate(BaseModel):
    name: str | None = None
    abbreviation: str | None = None
    description: str | None = None
    is_official: bool | None = None


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


class RuleSearchResult(BaseModel):
    id: int
    type: str | None = None
    slug: str
    ruleset_id: int
    ruleset_name: str
    rule_name: str
    rule_description: str | None = None
    tags: list[str] | None = None
    changes_description: str | None = None
    is_official: bool = False
    created_at: datetime
    updated_at: datetime
    created_by: str | None = None
    last_update_by: str | None = None
