"""Tests for the rules API endpoints."""


class TestRulesAPI:
    """Test rules CRUD API endpoints."""

    def test_list_rules_empty(self, client):
        """Test listing rules returns empty list when no rules exist."""
        response = client.get("/api/rules")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_rules_with_sample(self, client, sample_rule):
        """Test listing rules returns the sample rule."""
        response = client.get("/api/rules")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name_en"] == "Test Fireball"
        assert data[0]["type"] == "spell"

    def test_create_rule_without_auth(self, client, sample_ruleset):
        """Test creating rule without authentication fails."""
        rule_data = {
            "name_en": "New Spell",
            "description_en": "A new spell",
            "type": "spell",
            "ruleset_id": sample_ruleset.id,
        }
        response = client.post("/api/rules/", json=rule_data)
        assert response.status_code == 401

    def test_create_rule_with_auth(self, authenticated_client, sample_ruleset):
        """Test creating rule with authentication succeeds."""
        rule_data = {
            "name_en": "Ice Bolt",
            "description_en": "A cold damage spell",
            "type": "spell",
            "tags": ["cold", "magic"],
            "ruleset_id": sample_ruleset.id,
        }
        response = authenticated_client.post("/api/rules/", json=rule_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name_en"] == "Ice Bolt"
        assert data["type"] == "spell"
        assert "id" in data

    def test_create_rule_invalid_ruleset(self, authenticated_client):
        """Test creating rule with invalid ruleset fails."""
        rule_data = {
            "name_en": "Invalid Rule",
            "description_en": "Rule with invalid ruleset",
            "type": "spell",
            "ruleset_id": 99999,
        }
        response = authenticated_client.post("/api/rules/", json=rule_data)
        assert response.status_code == 404
        assert "RuleSet not found" in response.json()["detail"]

    def test_get_rule_by_id(self, client, sample_rule):
        """Test getting a specific rule by ID."""
        response = client.get(f"/api/rules/{sample_rule.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_rule.id
        assert data["name_en"] == "Test Fireball"

    def test_get_rule_not_found(self, client):
        """Test getting non-existent rule returns 404."""
        response = client.get("/api/rules/99999")
        assert response.status_code == 404

    def test_list_rules_with_type_filter(self, client, sample_rule):
        """Test filtering rules by type."""
        response = client.get("/api/rules?type=spell")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "spell"

    def test_list_rules_with_pagination(self, client, sample_rule):
        """Test pagination parameters."""
        response = client.get("/api/rules?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10

    def test_update_rule_without_auth(self, client, sample_rule):
        """Test updating rule without authentication fails."""
        update_data = {"name_en": "Updated Fireball"}
        response = client.patch(f"/api/rules/{sample_rule.id}", json=update_data)
        assert response.status_code == 401

    def test_update_rule_with_auth(self, authenticated_client, sample_rule):
        """Test updating rule with authentication succeeds."""
        update_data = {"name_en": "Greater Fireball", "description_en": sample_rule.description_en}
        response = authenticated_client.patch(f"/api/rules/{sample_rule.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name_en"] == "Greater Fireball"
        assert data["type"] == "spell"  # Other fields unchanged

    def test_delete_rule_without_auth(self, client, sample_rule):
        """Test deleting rule without authentication fails."""
        response = client.delete(f"/api/rules/{sample_rule.id}")
        assert response.status_code == 401

    def test_delete_rule_with_auth(self, authenticated_client, sample_rule):
        """Test deleting rule with authentication succeeds."""
        rule_id = sample_rule.id
        response = authenticated_client.delete(f"/api/rules/{rule_id}")
        assert response.status_code == 204

        # Verify rule is deleted
        get_response = authenticated_client.get(f"/api/rules/{rule_id}")
        assert get_response.status_code == 404
