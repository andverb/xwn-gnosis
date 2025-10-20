"""
Search service for building fuzzy search queries using PostgreSQL trigram similarity.

This module provides reusable functions for constructing complex search queries
with multi-word support and weighted field scoring.

## Future Enhancement: Domain-Specific Synonyms
To improve searches like "necromancer spells" → "necromancy spells", consider adding:

SEARCH_SYNONYMS = {
    "necromancer": ["necromancy", "necromancer", "necro"],
    "elementalist": ["elemental", "elementalist"],
    "high mage": ["high magic", "high mage"],
}

Then expand query terms before searching. See CLAUDE.md for full implementation notes.
"""

from sqlalchemy import String, func, or_
from sqlalchemy.sql.elements import ColumnElement

from app import models


def build_fuzzy_search_query(
    search_query: str,
    min_similarity: float = 0.1,
) -> tuple[ColumnElement, ColumnElement]:
    """
    Build fuzzy search conditions and similarity scoring for Rule model.

    This function creates SQLAlchemy expressions for:
    1. Similarity scoring across multiple fields (names, descriptions, type, tags)
    2. WHERE conditions using trigram matching

    For multi-word queries (e.g., "vowed arts"), it:
    - Splits the query into individual words
    - Calculates similarity for each word across all fields
    - Sums the scores (items matching multiple words rank higher)

    Args:
        search_query: The search string (can be single or multi-word)
        min_similarity: Minimum similarity threshold (0.0-1.0)

    Returns:
        tuple: (similarity_score_expression, where_condition_expression)
            - similarity_score_expression: SQLAlchemy labeled expression for ORDER BY
            - where_condition_expression: SQLAlchemy expression for WHERE clause

    Example:
        >>> similarity_score, where_condition = build_fuzzy_search_query("vowed arts")
        >>> stmt = select(Rule, similarity_score).where(where_condition)
    """
    search_query = search_query.lower()
    search_words = search_query.split()

    # Multi-word search: sum similarity scores for each word
    if len(search_words) > 1:
        word_scores = []
        word_conditions = []

        for word in search_words:
            # Calculate similarity for this word across all searchable fields
            # Weights: Names (2x), Type (3x), Tags (2x), Descriptions (1x)
            word_score = func.greatest(
                func.similarity(func.lower(models.Rule.name_en), word) * 2,
                func.similarity(func.lower(models.Rule.name_uk), word) * 2,
                func.similarity(func.lower(models.Rule.type), word) * 3,
                func.similarity(func.lower(models.Rule.tags.cast(String)), word) * 2,
                func.similarity(func.lower(models.Rule.description_en), word),
                func.similarity(func.lower(models.Rule.description_uk), word),
            )
            word_scores.append(word_score)

            # Add WHERE conditions for this word (match in any field)
            word_conditions.extend(
                [
                    func.lower(models.Rule.name_en).op("%")(word),
                    func.lower(models.Rule.name_uk).op("%")(word),
                    func.lower(models.Rule.description_en).op("%")(word),
                    func.lower(models.Rule.description_uk).op("%")(word),
                    models.Rule.tags.cast(String).ilike(f"%{word}%"),
                    models.Rule.type.ilike(f"%{word}%"),
                ]
            )

        # Sum all word scores for final similarity score
        similarity_score = sum(word_scores).label("similarity_score")
        where_condition = or_(*word_conditions)

    else:
        # Single word search
        name_en_sim = func.similarity(func.lower(models.Rule.name_en), search_query)
        name_uk_sim = func.similarity(func.lower(models.Rule.name_uk), search_query)
        desc_en_sim = func.similarity(func.lower(models.Rule.description_en), search_query)
        desc_uk_sim = func.similarity(func.lower(models.Rule.description_uk), search_query)
        type_sim = func.similarity(func.lower(models.Rule.type), search_query)
        tags_sim = func.similarity(func.lower(models.Rule.tags.cast(String)), search_query)

        # Use the best similarity score from any field with weighted importance
        similarity_score = func.greatest(
            name_en_sim * 2,
            name_uk_sim * 2,
            type_sim * 5,
            tags_sim * 3,
            desc_en_sim,
            desc_uk_sim,
        ).label("similarity_score")

        # WHERE condition: match in any field
        where_condition = or_(
            func.lower(models.Rule.name_en).op("%")(search_query),
            func.lower(models.Rule.name_uk).op("%")(search_query),
            func.lower(models.Rule.description_en).op("%")(search_query),
            func.lower(models.Rule.description_uk).op("%")(search_query),
            models.Rule.tags.cast(String).ilike(f"%{search_query}%"),
            models.Rule.type.ilike(f"%{search_query}%"),
        )

    # Add minimum similarity threshold to WHERE condition
    where_condition = where_condition & (similarity_score >= min_similarity)

    return similarity_score, where_condition
