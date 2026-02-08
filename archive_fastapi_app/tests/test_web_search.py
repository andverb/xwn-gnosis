"""Tests for the web search endpoints.

Note: Full search functionality requires PostgreSQL with pg_trgm extension.
Web search routes require database access, so they cannot be tested with SQLite.
These endpoints are tested in integration/E2E tests with real PostgreSQL.
"""
