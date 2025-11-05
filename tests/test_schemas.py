"""
Tests for Pydantic schemas and validation.

This module tests data validation logic in app/schemas.py.
"""

import pytest
from pydantic import ValidationError

from app import schemas


class TestRuleSchemas:
    """Test Rule schema validation."""

    def test_rule_base_valid(self):
        """Test creating a valid RuleBase."""
        rule = schemas.RuleBase(
            name_en="Test Rule",
            description_en="A test rule description",
            type="spell",
            tags=["magic", "test"],
        )
        assert rule.name_en == "Test Rule"
        assert rule.description_en == "A test rule description"
        assert rule.type == "spell"
        assert rule.tags == ["magic", "test"]

    def test_rule_base_strips_whitespace(self):
        """Test that whitespace is stripped from names and descriptions."""
        rule = schemas.RuleBase(
            name_en="  Test Rule  ",
            description_en="  A test description  ",
            name_uk="  Тестове правило  ",
            description_uk="  Тестовий опис  ",
        )
        assert rule.name_en == "Test Rule"
        assert rule.description_en == "A test description"
        assert rule.name_uk == "Тестове правило"
        assert rule.description_uk == "Тестовий опис"

    def test_rule_base_empty_name_fails(self):
        """Test that empty English name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.RuleBase(
                name_en="   ",
                description_en="Valid description",
            )
        assert "name_en" in str(exc_info.value)

    def test_rule_base_empty_description_fails(self):
        """Test that empty English description raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.RuleBase(
                name_en="Valid Name",
                description_en="   ",
            )
        assert "description_en" in str(exc_info.value)

    def test_rule_type_validation(self):
        """Test that invalid rule types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.RuleBase(
                name_en="Test",
                description_en="Test",
                type="invalid_type",
            )
        assert "type" in str(exc_info.value)
        assert "invalid_type" in str(exc_info.value)

    def test_rule_type_valid_types(self):
        """Test that all valid rule types are accepted."""
        valid_types = [
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
        ]
        for rule_type in valid_types:
            rule = schemas.RuleBase(
                name_en="Test",
                description_en="Test",
                type=rule_type,
            )
            assert rule.type == rule_type

    def test_rule_tags_deduplicated_and_sorted(self):
        """Test that duplicate tags are removed and sorted."""
        rule = schemas.RuleBase(
            name_en="Test",
            description_en="Test",
            tags=["combat", "magic", "combat", "armor"],
        )
        assert rule.tags == ["armor", "combat", "magic"]

    def test_rule_tags_normalized_to_lowercase(self):
        """Test that tags are converted to lowercase."""
        rule = schemas.RuleBase(
            name_en="Test",
            description_en="Test",
            tags=["Combat", "MAGIC", "Armor"],
        )
        assert rule.tags == ["armor", "combat", "magic"]

    def test_rule_tags_empty_tags_rejected(self):
        """Test that empty tag strings are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.RuleBase(
                name_en="Test",
                description_en="Test",
                tags=["valid", "", "  "],
            )
        assert "tags" in str(exc_info.value)

    def test_rule_create_requires_ruleset_id(self):
        """Test that RuleCreate requires ruleset_id."""
        rule = schemas.RuleCreate(
            name_en="Test",
            description_en="Test",
            ruleset_id=1,
        )
        assert rule.ruleset_id == 1

    def test_rule_update_all_fields_optional(self):
        """Test that RuleUpdate allows partial updates."""
        # Should be valid with no fields
        rule = schemas.RuleUpdate()
        assert rule.name_en is None

        # Should be valid with only some fields
        rule = schemas.RuleUpdate(name_en="New Name")
        assert rule.name_en == "New Name"
        assert rule.description_en is None


class TestRuleSetSchemas:
    """Test RuleSet schema validation."""

    def test_ruleset_base_valid(self):
        """Test creating a valid RuleSetBase."""
        ruleset = schemas.RuleSetBase(
            name="Test Ruleset",
            abbreviation="TR",
            description="A test ruleset",
            is_official=True,
        )
        assert ruleset.name == "Test Ruleset"
        assert ruleset.abbreviation == "TR"
        assert ruleset.is_official is True

    def test_ruleset_name_strips_whitespace(self):
        """Test that ruleset name whitespace is stripped."""
        ruleset = schemas.RuleSetBase(
            name="  Test Ruleset  ",
        )
        assert ruleset.name == "Test Ruleset"

    def test_ruleset_empty_name_fails(self):
        """Test that empty ruleset name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.RuleSetBase(name="   ")
        assert "name" in str(exc_info.value)

    def test_ruleset_name_too_short_fails(self):
        """Test that ruleset name must be at least 3 characters."""
        with pytest.raises(ValidationError) as exc_info:
            schemas.RuleSetBase(name="AB")
        assert "name" in str(exc_info.value)

    def test_ruleset_default_is_official_false(self):
        """Test that is_official defaults to False."""
        ruleset = schemas.RuleSetBase(name="Test")
        assert ruleset.is_official is False

    def test_ruleset_create_with_base_ruleset_id(self):
        """Test creating ruleset with base_ruleset_id for homebrew."""
        ruleset = schemas.RuleSetCreate(
            name="Test Homebrew",
            base_ruleset_id=1,
        )
        assert ruleset.base_ruleset_id == 1

    def test_ruleset_update_all_optional(self):
        """Test that RuleSetUpdate allows partial updates."""
        ruleset = schemas.RuleSetUpdate()
        assert ruleset.name is None
        assert ruleset.is_official is None


class TestRuleSearchResult:
    """Test RuleSearchResult schema."""

    def test_rule_search_result_structure(self):
        """Test that RuleSearchResult has correct structure."""
        from datetime import datetime

        result = schemas.RuleSearchResult(
            id=1,
            type="spell",
            slug="test-spell",
            ruleset_id=1,
            ruleset_name="Test Ruleset",
            rule_name="Test Spell",
            rule_description="A test spell",
            tags=["magic"],
            is_official=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert result.id == 1
        assert result.rule_name == "Test Spell"
        assert result.ruleset_name == "Test Ruleset"
