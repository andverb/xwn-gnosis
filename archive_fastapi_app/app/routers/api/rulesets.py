from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app import models, schemas
from app.dependencies import DbSession
from app.dependencies.auth import verify_admin_credentials

router = APIRouter(prefix="/api/rulesets", tags=["rulesets-api"])


@router.post("/", response_model=schemas.RuleSet, dependencies=[Depends(verify_admin_credentials)])
async def create_ruleset(ruleset: schemas.RuleSetCreate, db: DbSession):
    if ruleset.base_ruleset_id is not None:
        stmt = select(models.RuleSet).where(models.RuleSet.id == ruleset.base_ruleset_id)
        result = await db.execute(stmt)
        base_ruleset = result.scalar_one_or_none()
        if base_ruleset is None:
            raise HTTPException(status_code=404, detail="Base RuleSet not found")

    db_ruleset = models.RuleSet(**ruleset.model_dump())
    db.add(db_ruleset)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A ruleset with this name already exists",
        )

    await db.refresh(db_ruleset)
    return db_ruleset


@router.get("/", response_model=list[schemas.RuleSet])
async def list_rulesets(db: DbSession, skip: int = 0, limit: int = 100):
    stmt = select(models.RuleSet).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{ruleset_id}", response_model=schemas.RuleSet)
async def get_ruleset(ruleset_id: int, db: DbSession):
    stmt = select(models.RuleSet).where(models.RuleSet.id == ruleset_id)
    result = await db.execute(stmt)
    ruleset = result.scalar_one_or_none()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return ruleset


@router.put("/{ruleset_id}", response_model=schemas.RuleSet, dependencies=[Depends(verify_admin_credentials)])
async def update_ruleset(ruleset_id: int, ruleset_update: schemas.RuleSetUpdate, db: DbSession):
    stmt = select(models.RuleSet).where(models.RuleSet.id == ruleset_id)
    result = await db.execute(stmt)
    ruleset = result.scalar_one_or_none()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")

    update_data = ruleset_update.model_dump(exclude_unset=True)

    # FK validation if base_ruleset_id is being updated
    if "base_ruleset_id" in update_data:
        stmt = select(models.RuleSet).where(models.RuleSet.id == update_data["base_ruleset_id"])
        result = await db.execute(stmt)
        base_ruleset = result.scalar_one_or_none()
        if base_ruleset is None:
            raise HTTPException(status_code=404, detail="Base RuleSet not found")

    for field, value in update_data.items():
        setattr(ruleset, field, value)

    # TODO proper user implementation. Model populates only at creation
    ruleset.last_update_by = "sorcerer-king-admin"

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A ruleset with this name already exists",
        )

    await db.refresh(ruleset)
    return ruleset


@router.delete("/{ruleset_id}", status_code=204, dependencies=[Depends(verify_admin_credentials)])
async def delete_ruleset(ruleset_id: int, db: DbSession, cascade: bool = False):
    """
    Delete a ruleset.

    - **cascade**: If true, also delete all rules associated with this ruleset.
                   If false (default) and rules exist, returns 409 Conflict error.
    """
    stmt = select(models.RuleSet).where(models.RuleSet.id == ruleset_id)
    result = await db.execute(stmt)
    ruleset = result.scalar_one_or_none()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")

    # Count associated rules
    count_stmt = select(models.Rule).where(models.Rule.ruleset_id == ruleset_id)
    count_result = await db.execute(count_stmt)
    rules = count_result.scalars().all()
    rules_count = len(rules)

    # If rules exist and cascade is not enabled, return 409 Conflict
    if rules_count > 0 and not cascade:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete ruleset with {rules_count} associated rule{'s' if rules_count != 1 else ''}. "
            f"Use ?cascade=true to delete ruleset and all associated rules.",
        )

    # Cascade delete: delete rules first, then ruleset (in a single transaction)
    if cascade and rules_count > 0:
        delete_rules_stmt = delete(models.Rule).where(models.Rule.ruleset_id == ruleset_id)
        await db.execute(delete_rules_stmt)

    # Delete the ruleset
    await db.delete(ruleset)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete ruleset due to database constraint violation",
        )
