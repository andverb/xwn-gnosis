"""Tests for the rulesets API endpoints."""


class TestRulesetsAPI:
    """Test rulesets CRUD API endpoints."""

    def test_list_rulesets_empty(self, client):
        """Test listing rulesets returns empty list when none exist."""
        response = client.get("/api/rulesets")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_rulesets_with_sample(self, client, sample_ruleset):
        """Test listing rulesets returns the sample ruleset."""
        response = client.get("/api/rulesets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Worlds Without Number"
        assert data[0]["abbreviation"] == "Test-WWN"

    def test_create_ruleset_without_auth(self, client):
        """Test creating ruleset without authentication fails."""
        ruleset_data = {
            "name": "New Ruleset",
            "abbreviation": "NRS",
            "description": "A test ruleset",
        }
        response = client.post("/api/rulesets/", json=ruleset_data)
        assert response.status_code == 401

    def test_create_ruleset_with_auth(self, authenticated_client):
        """Test creating ruleset with authentication succeeds."""
        ruleset_data = {
            "name": "Stars Without Number",
            "abbreviation": "SWN",
            "description": "A sci-fi RPG ruleset",
        }
        response = authenticated_client.post("/api/rulesets/", json=ruleset_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Stars Without Number"
        assert data["abbreviation"] == "SWN"
        assert "id" in data

    def test_get_ruleset_by_id(self, client, sample_ruleset):
        """Test getting a specific ruleset by ID."""
        response = client.get(f"/api/rulesets/{sample_ruleset.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_ruleset.id
        assert data["name"] == "Test Worlds Without Number"

    def test_get_ruleset_not_found(self, client):
        """Test getting non-existent ruleset returns 404."""
        response = client.get("/api/rulesets/99999")
        assert response.status_code == 404

    def test_update_ruleset_without_auth(self, client, sample_ruleset):
        """Test updating ruleset without authentication fails."""
        update_data = {"name": "Updated Ruleset", "abbreviation": "UPD"}
        response = client.put(f"/api/rulesets/{sample_ruleset.id}", json=update_data)
        assert response.status_code == 401

    def test_update_ruleset_with_auth(self, authenticated_client, sample_ruleset):
        """Test updating ruleset with authentication succeeds."""
        update_data = {"description": "Updated description"}
        response = authenticated_client.put(f"/api/rulesets/{sample_ruleset.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_ruleset_without_auth(self, client, sample_ruleset):
        """Test deleting ruleset without authentication fails."""
        response = client.delete(f"/api/rulesets/{sample_ruleset.id}")
        assert response.status_code == 401

    def test_delete_ruleset_with_auth(self, authenticated_client, sample_ruleset):
        """Test deleting ruleset with authentication succeeds."""
        ruleset_id = sample_ruleset.id
        response = authenticated_client.delete(f"/api/rulesets/{ruleset_id}")
        assert response.status_code == 204

        # Verify ruleset is deleted
        get_response = authenticated_client.get(f"/api/rulesets/{ruleset_id}")
        assert get_response.status_code == 404

    def test_create_ruleset_duplicate_name(self, authenticated_client, sample_ruleset):
        """Test creating ruleset with duplicate name returns 409 Conflict."""
        ruleset_data = {
            "name": sample_ruleset.name,  # Same as sample_ruleset
            "abbreviation": "DUP",
            "description": "Should fail due to duplicate name",
        }
        response = authenticated_client.post("/api/rulesets/", json=ruleset_data)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_delete_ruleset_with_rules_without_cascade(self, authenticated_client, sample_ruleset, sample_rule):
        """Test deleting ruleset with associated rules without cascade returns 409."""
        response = authenticated_client.delete(f"/api/rulesets/{sample_ruleset.id}")
        assert response.status_code == 409
        assert "Cannot delete ruleset" in response.json()["detail"]
        assert "associated rule" in response.json()["detail"]
        assert "cascade=true" in response.json()["detail"]

        # Verify ruleset still exists
        get_response = authenticated_client.get(f"/api/rulesets/{sample_ruleset.id}")
        assert get_response.status_code == 200

        # Verify rule still exists
        rule_response = authenticated_client.get(f"/api/rules/{sample_rule.id}")
        assert rule_response.status_code == 200

    def test_delete_ruleset_with_rules_with_cascade(self, authenticated_client, sample_ruleset, sample_rule):
        """Test deleting ruleset with associated rules using cascade=true succeeds."""
        ruleset_id = sample_ruleset.id
        rule_id = sample_rule.id

        response = authenticated_client.delete(f"/api/rulesets/{ruleset_id}?cascade=true")
        assert response.status_code == 204

        # Verify ruleset is deleted
        get_response = authenticated_client.get(f"/api/rulesets/{ruleset_id}")
        assert get_response.status_code == 404

        # Verify rule is also deleted
        rule_response = authenticated_client.get(f"/api/rules/{rule_id}")
        assert rule_response.status_code == 404

    def test_delete_empty_ruleset_with_cascade_true(self, authenticated_client, sample_ruleset):
        """Test deleting empty ruleset with cascade=true succeeds."""
        ruleset_id = sample_ruleset.id
        response = authenticated_client.delete(f"/api/rulesets/{ruleset_id}?cascade=true")
        assert response.status_code == 204

        # Verify ruleset is deleted
        get_response = authenticated_client.get(f"/api/rulesets/{ruleset_id}")
        assert get_response.status_code == 404

    def test_delete_empty_ruleset_with_cascade_false(self, authenticated_client, sample_ruleset):
        """Test deleting empty ruleset with cascade=false succeeds."""
        ruleset_id = sample_ruleset.id
        response = authenticated_client.delete(f"/api/rulesets/{ruleset_id}?cascade=false")
        assert response.status_code == 204

        # Verify ruleset is deleted
        get_response = authenticated_client.get(f"/api/rulesets/{ruleset_id}")
        assert get_response.status_code == 404
