# Gnosis Test Suite

This directory contains the test suite for the Gnosis application.

## Test Structure

```
tests/
├── conftest.py           # Pytest configuration and shared fixtures
├── test_api_health.py    # Health check and basic API tests
├── test_models.py        # SQLAlchemy model tests
├── test_schemas.py       # Pydantic schema validation tests
└── test_utils.py         # Utility function tests
```

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with coverage
```bash
uv run pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
uv run pytest tests/test_schemas.py
```

### Run specific test class or function
```bash
uv run pytest tests/test_schemas.py::TestRuleSchemas::test_rule_base_valid
```

### Run tests with specific markers
```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration
```

### Run tests in parallel (faster)
```bash
uv run pytest -n auto
```

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `test_settings`: Test configuration with test database URL
- `test_engine`: SQLAlchemy async engine for tests
- `db_session`: Database session for each test (auto-rollback)
- `client`: FastAPI TestClient with dependency overrides
- `sample_ruleset`: Pre-created test ruleset
- `sample_rule`: Pre-created test rule
- `auth_headers`: HTTP Basic Auth headers for authenticated requests
- `api_key_headers`: API key headers for authenticated requests

## Writing Tests

### Example: Testing a Pydantic schema
```python
def test_rule_validation():
    rule = schemas.RuleBase(
        name_en="Test Rule",
        description_en="Test description"
    )
    assert rule.name_en == "Test Rule"
```

### Example: Testing a database model
```python
@pytest.mark.asyncio
async def test_create_rule(db_session, sample_ruleset):
    rule = Rule(
        name_en="Test",
        description_en="Test",
        ruleset_id=sample_ruleset.id
    )
    db_session.add(rule)
    await db_session.commit()
    assert rule.id is not None
```

### Example: Testing an API endpoint
```python
def test_get_rule(client, sample_rule):
    response = client.get(f"/api/rules/{sample_rule.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name_en"] == sample_rule.name_en
```

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test session
- Fast and isolated
- Automatically cleaned up after tests

This is different from the production PostgreSQL database.

## Continuous Integration

Tests should be run in CI/CD pipelines to ensure code quality:

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: uv run pytest --cov=app
```

## Coverage Goals

Aim for:
- **>80% overall code coverage**
- **100% coverage for critical paths** (authentication, data validation)
- **All public API endpoints tested**

## Test Categories

Tests are marked with categories:
- `@pytest.mark.unit` - Fast unit tests with no external dependencies
- `@pytest.mark.integration` - Integration tests requiring database
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slow-running tests

Use these markers to selectively run subsets of tests during development.
