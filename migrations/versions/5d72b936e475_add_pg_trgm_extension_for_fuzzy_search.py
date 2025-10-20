"""add_pg_trgm_extension_for_fuzzy_search

Revision ID: 5d72b936e475
Revises: 84406a33d882
Create Date: 2025-10-20 20:28:30.789980

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5d72b936e475"
down_revision: str | Sequence[str] | None = "84406a33d882"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pg_trgm extension for fuzzy text search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Create GIN indexes for trigram similarity search on name and description fields
    # These indexes significantly speed up similarity searches
    op.execute("CREATE INDEX IF NOT EXISTS idx_rules_name_en_trgm ON rules USING gin (name_en gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_rules_name_uk_trgm ON rules USING gin (name_uk gin_trgm_ops)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_rules_description_en_trgm ON rules USING gin (description_en gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_rules_description_uk_trgm ON rules USING gin (description_uk gin_trgm_ops)"
    )

    # Create GIN index for type field (short string, good for exact and fuzzy matching)
    op.execute("CREATE INDEX IF NOT EXISTS idx_rules_type_trgm ON rules USING gin (type gin_trgm_ops)")

    # Note: tags is a JSON field, so we'll search it by casting to text in queries
    # No separate index needed as the cast happens at query time


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_rules_name_en_trgm")
    op.execute("DROP INDEX IF EXISTS idx_rules_name_uk_trgm")
    op.execute("DROP INDEX IF EXISTS idx_rules_description_en_trgm")
    op.execute("DROP INDEX IF EXISTS idx_rules_description_uk_trgm")
    op.execute("DROP INDEX IF EXISTS idx_rules_type_trgm")

    # Drop extension (only if no other tables use it)
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
