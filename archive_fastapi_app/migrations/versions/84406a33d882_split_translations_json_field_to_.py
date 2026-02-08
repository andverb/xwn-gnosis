"""split translations json field to separate language fields

Revision ID: 84406a33d882
Revises: 409125800384
Create Date: 2025-10-15 10:36:27.893672

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "84406a33d882"
down_revision: str | Sequence[str] | None = "409125800384"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: Split translations JSON to separate fields."""
    # Add new columns (nullable initially to allow data migration)
    op.add_column("rules", sa.Column("name_en", sa.String(length=200), nullable=True))
    op.add_column("rules", sa.Column("description_en", sa.Text(), nullable=True))
    op.add_column("rules", sa.Column("name_uk", sa.String(length=200), nullable=True))
    op.add_column("rules", sa.Column("description_uk", sa.Text(), nullable=True))

    # Migrate data from JSON to separate columns
    connection = op.get_bind()

    # Get all rules
    result = connection.execute(sa.text("SELECT id, translations FROM rules"))
    rules = result.fetchall()

    # Update each rule
    for rule_id, translations_json in rules:
        if translations_json:
            # Extract English content
            en_name = translations_json.get("en", {}).get("name", "")
            en_description = translations_json.get("en", {}).get("description", "")

            # Extract Ukrainian content
            uk_name = translations_json.get("uk", {}).get("name")
            uk_description = translations_json.get("uk", {}).get("description")

            # Update the row
            connection.execute(
                sa.text(
                    """
                    UPDATE rules
                    SET name_en = :name_en,
                        description_en = :description_en,
                        name_uk = :name_uk,
                        description_uk = :description_uk
                    WHERE id = :rule_id
                    """
                ),
                {
                    "name_en": en_name,
                    "description_en": en_description,
                    "name_uk": uk_name,
                    "description_uk": uk_description,
                    "rule_id": rule_id,
                },
            )

    # Make English fields non-nullable now that data is migrated
    op.alter_column("rules", "name_en", nullable=False)
    op.alter_column("rules", "description_en", nullable=False)

    # Drop the old translations column
    op.drop_column("rules", "translations")


def downgrade() -> None:
    """Downgrade schema: Restore translations JSON from separate fields."""
    # Add back the translations JSON column
    op.add_column(
        "rules",
        sa.Column("translations", sa.dialects.postgresql.JSON(), nullable=True),
    )

    # Migrate data back to JSON format
    connection = op.get_bind()

    # Get all rules with separate fields
    result = connection.execute(sa.text("SELECT id, name_en, description_en, name_uk, description_uk FROM rules"))
    rules = result.fetchall()

    # Update each rule
    for rule_id, name_en, description_en, name_uk, description_uk in rules:
        translations = {"en": {"name": name_en, "description": description_en}}

        if name_uk or description_uk:
            translations["uk"] = {
                "name": name_uk or "",
                "description": description_uk or "",
            }

        # Update the row with JSON
        connection.execute(
            sa.text("UPDATE rules SET translations = :translations WHERE id = :rule_id"),
            {"translations": translations, "rule_id": rule_id},
        )

    # Make translations non-nullable
    op.alter_column("rules", "translations", nullable=False)

    # Drop the separate language columns
    op.drop_column("rules", "description_uk")
    op.drop_column("rules", "name_uk")
    op.drop_column("rules", "description_en")
    op.drop_column("rules", "name_en")
