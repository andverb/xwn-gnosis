from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RuleContent(BaseModel):
    name: str
    description: str


class RuleBase(BaseModel):
    rule_set: str
    tags: list[str] | None = None
    translations: dict[str, RuleContent]


class RuleCreate(RuleBase): ...


class RuleUpdate(BaseModel):
    rule_set: str | None = None
    tags: list[str] | None = None
    translations: dict[str, RuleContent] | None = None


class Rule(RuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    def get_content(self, lang: str = "en") -> RuleContent:
        """Get content for specific language, fallback to English"""
        content = self.translations.get(lang, self.translations.get("en"))
        if content is None:
            raise ValueError(f"No content available for language: {lang}")
        return RuleContent(**content) if isinstance(content, dict) else content
