from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import JSONB

from app import models, schemas
from app.dependencies import DbSession
from app.dependencies.auth import verify_admin_credentials

router = APIRouter(prefix="/api/rules", tags=["rules-api"])


@router.post("/", response_model=schemas.Rule, dependencies=[Depends(verify_admin_credentials)])
async def create_rule(rule: schemas.RuleCreate, db: DbSession):
    # Validate required ruleset_id
    stmt = select(models.RuleSet).where(models.RuleSet.id == rule.ruleset_id)
    result = await db.execute(stmt)
    ruleset = result.scalar_one_or_none()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="RuleSet not found")

    # Validate optional base_rule_id
    if rule.base_rule_id is not None:
        stmt = select(models.Rule).where(models.Rule.id == rule.base_rule_id)
        result = await db.execute(stmt)
        base_rule = result.scalar_one_or_none()
        if base_rule is None:
            raise HTTPException(status_code=404, detail="Base Rule not found")

    db_rule = models.Rule(**rule.model_dump())
    # Sync is_official from ruleset (we already have it loaded)
    db_rule.is_official = ruleset.is_official
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.get("/", response_model=list[schemas.Rule])
async def list_rules(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
    type: str | None = None,
    tags: str | None = None,
):
    """
    List rules with optional filters.

    - **type**: Filter by rule type (e.g., "class", "art", "skill")
    - **tags**: Comma-separated list of tags to filter by (e.g., "elementalist,art")
    """
    stmt = select(models.Rule)

    # Filter by type
    if type:
        stmt = stmt.where(models.Rule.type == type)

    # Filter by tags - check if ALL provided tags are in the rule's tags array
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            # Cast JSON to JSONB and use PostgreSQL's ? operator for containment check
            stmt = stmt.where(func.cast(models.Rule.tags, JSONB).contains([tag]))

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{rule_id}", response_model=schemas.Rule)
async def get_rule(rule_id: int, db: DbSession):
    stmt = select(models.Rule).where(models.Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=schemas.Rule, dependencies=[Depends(verify_admin_credentials)])
async def update_rule(rule_id: int, rule_update: schemas.RuleUpdate, db: DbSession):
    """Full update of a rule (all fields should be provided)."""
    stmt = select(models.Rule).where(models.Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = rule_update.model_dump(exclude_unset=True)
    # FK validation if ruleset_id is being updated
    if "ruleset_id" in update_data:
        stmt = select(models.RuleSet).where(models.RuleSet.id == update_data["ruleset_id"])
        result = await db.execute(stmt)
        ruleset = result.scalar_one_or_none()
        if ruleset is None:
            raise HTTPException(status_code=404, detail="RuleSet not found")

    for field, value in update_data.items():
        setattr(rule, field, value)

    # TODO proper user implementation. Model populates only at creation
    rule.last_update_by = "sorcerer-king-admin"

    await db.commit()
    await db.refresh(rule)
    return rule


@router.patch("/{rule_id}", response_model=schemas.Rule, dependencies=[Depends(verify_admin_credentials)])
async def partial_update_rule(rule_id: int, rule_update: schemas.RuleUpdate, db: DbSession):
    """
    Partial update of a rule - only update fields that are provided.
    Fields not provided in the request body will remain unchanged.
    """
    stmt = select(models.Rule).where(models.Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Only get fields that were explicitly provided in the request
    update_data = rule_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    # FK validation if ruleset_id is being updated
    if "ruleset_id" in update_data:
        stmt = select(models.RuleSet).where(models.RuleSet.id == update_data["ruleset_id"])
        result = await db.execute(stmt)
        ruleset = result.scalar_one_or_none()
        if ruleset is None:
            raise HTTPException(status_code=404, detail="RuleSet not found")

    # Apply only the provided fields
    for field, value in update_data.items():
        setattr(rule, field, value)

    # TODO proper user implementation. Model populates only at creation
    rule.last_update_by = "sorcerer-king-admin"

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", dependencies=[Depends(verify_admin_credentials)])
async def delete_rule(rule_id: int, db: DbSession):
    stmt = select(models.Rule).where(models.Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    await db.delete(rule)
    await db.commit()
    return {"message": "Rule deleted successfully"}
