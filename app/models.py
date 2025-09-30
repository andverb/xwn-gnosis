from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, event
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.utils import generate_slug

Base = declarative_base()


class RuleSet(Base):
    __tablename__ = "rulesets"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    slug = Column(String(100), nullable=False)
    description = Column(Text)

    # Relationships - one ruleset can have many homebrew versions rulesets, overriding some rules
    base_ruleset_id = Column(Integer, ForeignKey("rulesets.id"), nullable=True)
    base_ruleset = relationship(
        "RuleSet", remote_side="RuleSet.id", back_populates="homebrew_rulesets"
    )  # Points UP to parent
    homebrew_rulesets = relationship("RuleSet", back_populates="base_ruleset")  # Points DOWN to children

    # Relationships - one ruleset - to - many rules
    rules = relationship("Rule", back_populates="ruleset")

    # Autopopulated
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # TODO add users foreign keys
    created_by = Column(String(150), nullable=False, default="sorcerer-king-admin")
    last_update_by = Column(String(150), nullable=False, default="sorcerer-king-admin")


@event.listens_for(RuleSet, "before_insert")
def slugify_ruleset_name(mapper, connection, target):
    if target.name and not target.slug:
        target.slug = generate_slug(target.name)


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=True)  # e.g., spell, feat, equipment
    tags = Column(JSON, nullable=True)  # searchable tags like ["combat", "spells", "d20"]
    meta_data = Column(JSON, nullable=True)  # type-specific structured data
    # mechanics = Column(JSON, nullable=True)  #TODO language-agnostic game mechanics
    translations = Column(JSON, nullable=False)  # multilingual content
    slug = Column(String(100), nullable=False)

    changes_description = Column(Text)  # what was changed from base rule
    is_official = Column(Boolean, default=False)  # Official vs homebrew

    # Relationships - one ruleset to many rules with RuleSet - we store which ruleset this rule belongs to
    ruleset_id = Column(Integer, ForeignKey("rulesets.id"), nullable=False)
    ruleset = relationship("RuleSet", back_populates="rules")

    # Relationships - one rule can have may homebrew versions - self-referential
    base_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    base_rule = relationship("Rule", remote_side="Rule.id", back_populates="homebrew_rules")  # Points UP to parent
    homebrew_rules = relationship("Rule", back_populates="base_rule")  # Points DOWN to children

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # TODO add users foreign keys
    created_by = Column(String(150), nullable=False, default="sorcerer-king-admin")
    last_update_by = Column(String(150), nullable=False, default="sorcerer-king-admin")

    def get_name(self) -> str:
        # Try to get English content
        en_content = self.translations.get("en", {})
        if isinstance(en_content, dict):
            return en_content.get("name", f"rule-{self.id or 'new'}")

        # Fallback to first available language
        for lang, content in self.translations.items():
            if isinstance(content, dict) and "name" in content:
                return content["name"]

        return f"rule-{self.id}"


@event.listens_for(Rule, "before_insert")
def slugify_rule_name(mapper, connection, target):
    if target.translations and not target.slug:
        rule_name = target.get_name()
        target.slug = generate_slug(rule_name)
