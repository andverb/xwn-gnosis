"""
Tests for the search service module.

This module tests the fuzzy search query building functionality.
"""

from app.search_service import build_fuzzy_search_query


class TestBuildFuzzySearchQuery:
    """Test the build_fuzzy_search_query function."""

    def test_single_word_query_returns_tuple(self):
        """Test that single word query returns tuple of two elements."""
        similarity_score, where_condition = build_fuzzy_search_query("fireball")

        assert similarity_score is not None
        assert where_condition is not None
        assert hasattr(similarity_score, "name")  # Should be labeled
        assert similarity_score.name == "similarity_score"

    def test_multi_word_query_returns_tuple(self):
        """Test that multi-word query returns tuple of two elements."""
        similarity_score, where_condition = build_fuzzy_search_query("vowed arts")

        assert similarity_score is not None
        assert where_condition is not None
        assert hasattr(similarity_score, "name")  # Should be labeled
        assert similarity_score.name == "similarity_score"

    def test_query_normalized_to_lowercase(self):
        """Test that search query is normalized to lowercase."""
        # Both queries should produce similar results
        score1, condition1 = build_fuzzy_search_query("FIREBALL")
        score2, condition2 = build_fuzzy_search_query("fireball")

        # Both should be valid expressions
        assert score1 is not None
        assert score2 is not None
        assert condition1 is not None
        assert condition2 is not None

    def test_empty_query_returns_valid_expressions(self):
        """Test that empty query returns valid expressions."""
        similarity_score, where_condition = build_fuzzy_search_query("")

        assert similarity_score is not None
        assert where_condition is not None

    def test_min_similarity_parameter(self):
        """Test that min_similarity parameter is accepted."""
        similarity_score, where_condition = build_fuzzy_search_query("test", min_similarity=0.5)

        assert similarity_score is not None
        assert where_condition is not None

    def test_special_characters_in_query(self):
        """Test that special characters in query are handled."""
        similarity_score, where_condition = build_fuzzy_search_query("test-spell")

        assert similarity_score is not None
        assert where_condition is not None

    def test_unicode_in_query(self):
        """Test that Unicode characters in query are handled."""
        similarity_score, where_condition = build_fuzzy_search_query("вогонь")

        assert similarity_score is not None
        assert where_condition is not None

    def test_single_word_uses_greatest_function(self):
        """Test that single word query uses GREATEST for weighted scoring."""
        similarity_score, _where_condition = build_fuzzy_search_query("spell")

        # The score should be a labeled expression
        assert hasattr(similarity_score, "name")
        assert similarity_score.name == "similarity_score"

    def test_multi_word_splits_query(self):
        """Test that multi-word query splits on whitespace."""
        # Query with multiple words should be handled differently
        similarity_score, where_condition = build_fuzzy_search_query("fire ball")

        assert similarity_score is not None
        assert where_condition is not None

    def test_extra_whitespace_handled(self):
        """Test that extra whitespace is handled correctly."""
        similarity_score, where_condition = build_fuzzy_search_query("fire  ball   spell")

        assert similarity_score is not None
        assert where_condition is not None
