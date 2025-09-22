from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.utils import generate_slug

Base = declarative_base()


class RuleSet(Base):
    __tablename__ = "rulesets"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(100), nullable=False)
    description = Column(Text)

    # Relationships - homebrew rulesets inherit from base rulesets, overriding some rules
    base_ruleset_id = Column(Integer, ForeignKey("rulesets.id"), nullable=True)
    base_ruleset = relationship("RuleSet", remote_side="id")  # Points UP to parent
    homebrew_rulesets = relationship("RuleSet", back_populates="base_ruleset")  # Points DOWN to children

    # Relationships - one - to - many with rules
    rules = relationship("Rule", back_populates="base_ruleset")

    # Autopopulated
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    # TODO add users foreign keys
    created_by = Column(String(150), nullable=False)
    last_update_by = Column(String(150), nullable=False)


@event.listens_for(RuleSet, "before_insert")
def slugify_ruleset_name(mapper, connection, target):
    if target.name and not target.slug:
        target.slug = generate_slug(target.name)


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_set = Column(String(50), nullable=False)
    tags = Column(JSON, nullable=True)  # searchable tags like ["combat", "spells", "d20"]
    # mechanics = Column(JSON, nullable=True)  #TODO language-agnostic game mechanics
    translations = Column(JSON, nullable=False)  # multilingual content
    slug = Column(String(100), nullable=False)

    changes_description = Column(Text)  # what was changed from base rule
    is_official = Column(Boolean, default=False)  # Official vs homebrew

    # Relationships - one to many with RuleSet - we store which ruleset this rule belongs to
    ruleset_id = Column(Integer, ForeignKey("rulesets.id"), nullable=False)
    ruleset = relationship("RuleSet", back_populates="rules")

    # Relationships - self-referential, we store which base rule homebrew rule is based on
    base_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    base_rule = relationship("Rule", remote_side="id")  # Points UP to parent
    homebrew_rules = relationship("Rule", back_populates="base_rule")  # Points DOWN to children

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # TODO add users foreign keys
    created_by = Column(String(150), nullable=False)
    last_update_by = Column(String(150), nullable=False)

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
