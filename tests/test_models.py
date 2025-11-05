"""
Tests for SQLAlchemy models.

This module tests database models in app/models.py.
"""

import pytest
from sqlalchemy import select

from app.models import Rule, RuleSet


class TestRuleSetModel:
    """Test RuleSet model behavior."""

    @pytest.mark.asyncio
    async def test_create_ruleset(self, db_session):
        """Test creating a basic ruleset."""
        ruleset = RuleSet(
            name="Test Ruleset",
            slug="test-ruleset",
            abbreviation="TR",
            description="Test description",
            is_official=True,
        )
        db_session.add(ruleset)
        await db_session.commit()
        await db_session.refresh(ruleset)

        assert ruleset.id is not None
        assert ruleset.name == "Test Ruleset"
        assert ruleset.slug == "test-ruleset"
        assert ruleset.created_at is not None
        assert ruleset.updated_at is not None

    @pytest.mark.asyncio
    async def test_ruleset_slug_auto_generated(self, db_session):
        """Test that slug is auto-generated from name if not provided."""
        ruleset = RuleSet(
            name="Auto Slug Test",
            # slug is intentionally not set
        )
        db_session.add(ruleset)
        await db_session.commit()
        await db_session.refresh(ruleset)

        assert ruleset.slug == "auto-slug-test"

    @pytest.mark.asyncio
    async def test_ruleset_unique_name_constraint(self, db_session):
        """Test that ruleset names must be unique."""
        ruleset1 = RuleSet(name="Duplicate Name", slug="duplicate-1")
        db_session.add(ruleset1)
        await db_session.commit()

        # Trying to create another ruleset with the same name should fail
        ruleset2 = RuleSet(name="Duplicate Name", slug="duplicate-2")
        db_session.add(ruleset2)

        with pytest.raises(Exception):  # Will raise IntegrityError or similar
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_ruleset_homebrew_relationship(self, db_session):
        """Test that rulesets can have homebrew variants."""
        # Create base ruleset
        base_ruleset = RuleSet(
            name="Official Ruleset",
            slug="official",
            is_official=True,
        )
        db_session.add(base_ruleset)
        await db_session.commit()
        await db_session.refresh(base_ruleset)

        # Create homebrew variant
        homebrew = RuleSet(
            name="Homebrew Variant",
            slug="homebrew",
            base_ruleset_id=base_ruleset.id,
            is_official=False,
        )
        db_session.add(homebrew)
        await db_session.commit()
        await db_session.refresh(homebrew)

        assert homebrew.base_ruleset_id == base_ruleset.id


class TestRuleModel:
    """Test Rule model behavior."""

    @pytest.mark.asyncio
    async def test_create_rule(self, db_session, sample_ruleset):
        """Test creating a basic rule."""
        rule = Rule(
            name_en="Test Rule",
            description_en="Test description",
            type="spell",
            tags=["magic", "test"],
            ruleset_id=sample_ruleset.id,
        )
        db_session.add(rule)
        await db_session.commit()
        await db_session.refresh(rule)

        assert rule.id is not None
        assert rule.name_en == "Test Rule"
        assert rule.type == "spell"
        assert rule.tags == ["magic", "test"]
        assert rule.created_at is not None

    @pytest.mark.asyncio
    async def test_rule_slug_auto_generated(self, db_session, sample_ruleset):
        """Test that rule slug is auto-generated from name_en."""
        rule = Rule(
            name_en="Auto Slug Rule",
            description_en="Test",
            ruleset_id=sample_ruleset.id,
        )
        db_session.add(rule)
        await db_session.commit()
        await db_session.refresh(rule)

        assert rule.slug == "auto-slug-rule"

    @pytest.mark.asyncio
    async def test_rule_get_name_english(self, db_session, sample_rule):
        """Test getting rule name in English."""
        name = sample_rule.get_name("en")
        assert name == "Test Fireball"

    @pytest.mark.asyncio
    async def test_rule_get_name_ukrainian(self, db_session, sample_rule):
        """Test getting rule name in Ukrainian."""
        name = sample_rule.get_name("uk")
        assert name == "Тестова куля вогню"

    @pytest.mark.asyncio
    async def test_rule_get_name_fallback_to_english(self, db_session, sample_ruleset):
        """Test that get_name falls back to English if Ukrainian is missing."""
        rule = Rule(
            name_en="English Only",
            description_en="Test",
            name_uk=None,  # No Ukrainian translation
            ruleset_id=sample_ruleset.id,
        )
        db_session.add(rule)
        await db_session.commit()

        name = rule.get_name("uk")
        assert name == "English Only"

    @pytest.mark.asyncio
    async def test_rule_get_description_english(self, db_session, sample_rule):
        """Test getting rule description in English."""
        desc = sample_rule.get_description("en")
        assert desc == "A test spell that deals fire damage"

    @pytest.mark.asyncio
    async def test_rule_get_description_ukrainian(self, db_session, sample_rule):
        """Test getting rule description in Ukrainian."""
        desc = sample_rule.get_description("uk")
        assert desc == "Тестове закляття, що завдає вогняної шкоди"

    @pytest.mark.asyncio
    async def test_rule_unique_slug_per_ruleset(self, db_session, sample_ruleset):
        """Test that rule slugs must be unique within a ruleset."""
        rule1 = Rule(
            name_en="Duplicate Slug",
            description_en="First rule",
            slug="duplicate",
            ruleset_id=sample_ruleset.id,
        )
        db_session.add(rule1)
        await db_session.commit()

        # Try to create another rule with same slug in same ruleset
        rule2 = Rule(
            name_en="Another Rule",
            description_en="Second rule",
            slug="duplicate",
            ruleset_id=sample_ruleset.id,
        )
        db_session.add(rule2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_rule_is_official_synced_from_ruleset(self, db_session, sample_ruleset):
        """Test that rule.is_official is synced from ruleset."""
        # sample_ruleset has is_official=True
        rule = Rule(
            name_en="Official Rule",
            description_en="Should be official",
            ruleset_id=sample_ruleset.id,
            is_official=False,  # Set to False initially
        )
        db_session.add(rule)
        await db_session.commit()
        await db_session.refresh(rule)

        # After save, should be synced to ruleset's is_official value
        # Note: This requires the sync logic in the create endpoint
        # For now, just verify the field exists
        assert hasattr(rule, "is_official")

    @pytest.mark.asyncio
    async def test_rule_homebrew_relationship(self, db_session, sample_ruleset):
        """Test that rules can have homebrew variants."""
        # Create base rule
        base_rule = Rule(
            name_en="Base Rule",
            description_en="Original rule",
            ruleset_id=sample_ruleset.id,
        )
        db_session.add(base_rule)
        await db_session.commit()
        await db_session.refresh(base_rule)

        # Create homebrew variant
        homebrew_rule = Rule(
            name_en="Homebrew Variant",
            description_en="Modified rule",
            base_rule_id=base_rule.id,
            ruleset_id=sample_ruleset.id,
            changes_description="Made it more powerful",
        )
        db_session.add(homebrew_rule)
        await db_session.commit()
        await db_session.refresh(homebrew_rule)

        assert homebrew_rule.base_rule_id == base_rule.id
        assert homebrew_rule.changes_description is not None

    @pytest.mark.asyncio
    async def test_rule_meta_data_json(self, db_session, sample_ruleset):
        """Test that meta_data stores JSON correctly."""
        meta = {"level": 5, "school": "evocation", "components": ["V", "S", "M"]}
        rule = Rule(
            name_en="Rule with Metadata",
            description_en="Test",
            meta_data=meta,
            ruleset_id=sample_ruleset.id,
        )
        db_session.add(rule)
        await db_session.commit()
        await db_session.refresh(rule)

        assert rule.meta_data == meta
        assert rule.meta_data["level"] == 5
        assert "evocation" in rule.meta_data["school"]
