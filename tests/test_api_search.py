"""Tests for the search API endpoints.

Note: Full search functionality requires PostgreSQL with pg_trgm extension.
These tests only verify API contract and basic validation.
"""


class TestSearchAPI:
    """Basic search API tests that work without PostgreSQL trigrams."""

    def test_search_rules_no_query(self, client):
        """Test search without query parameter fails."""
        response = client.get("/api/search/rules")
        assert response.status_code == 422  # Validation error

    def test_search_rules_query_too_short(self, client):
        """Test search with query shorter than 2 characters fails."""
        response = client.get("/api/search/rules?q=a")
        assert response.status_code == 422  # Validation error

    def test_search_rules_limit_max(self, client):
        """Test search limit cannot exceed maximum."""
        response = client.get("/api/search/rules?q=test&limit=999")
        assert response.status_code == 422  # Validation error

    def test_search_rules_min_similarity_validation(self, client):
        """Test min_similarity parameter validation."""
        # Valid range is 0.0 to 1.0
        response = client.get("/api/search/rules?q=test&min_similarity=2.0")
        assert response.status_code == 422  # Validation error
