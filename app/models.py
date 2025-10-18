from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, event
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
    slug = Column(String(100), nullable=False, unique=True)
    abbreviation = Column(String(20), nullable=True)
    description = Column(Text)
    is_official = Column(Boolean, default=False)

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


@event.listens_for(RuleSet, "before_update")
def sync_rules_is_official_on_ruleset_update(mapper, connection, target):
    """When ruleset.is_official changes, update all its rules"""
    from sqlalchemy import inspect, update  # noqa

    state = inspect(target)
    history = state.get_history("is_official", passive=True)

    # Only update if is_official actually changed
    if history.has_changes():
        connection.execute(update(Rule).where(Rule.ruleset_id == target.id).values(is_official=target.is_official))


class Rule(Base):
    __tablename__ = "rules"
    __table_args__ = (UniqueConstraint("ruleset_id", "slug", name="uq_rule_ruleset_slug"),)

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=True)  # e.g., spell, feat, equipment
    tags = Column(JSON, nullable=True)  # searchable tags like ["combat", "spells", "d20"]
    meta_data = Column(JSON, nullable=True)  # type-specific structured data
    # mechanics = Column(JSON, nullable=True)  #TODO language-agnostic game mechanics

    # Separate fields for each language (better for search and indexing)
    name_en = Column(String(200), nullable=False)
    description_en = Column(Text, nullable=False)
    name_uk = Column(String(200), nullable=True)
    description_uk = Column(Text, nullable=True)

    slug = Column(String(100), nullable=False)

    changes_description = Column(Text)  # what was changed from base rule
    is_official = Column(Boolean, default=False)  # Denormalized from ruleset for query performance

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

    def get_name(self, lang: str = "en") -> str:
        """Get rule name in specified language, fallback to English"""
        if lang == "uk" and self.name_uk:
            return self.name_uk
        return self.name_en or f"rule-{self.id or 'new'}"

    def get_description(self, lang: str = "en") -> str:
        """Get rule description in specified language, fallback to English"""
        if lang == "uk" and self.description_uk:
            return self.description_uk
        return self.description_en or ""


@event.listens_for(Rule, "before_insert")
def slugify_rule_name(mapper, connection, target):
    if target.name_en and not target.slug:
        target.slug = generate_slug(target.name_en)
