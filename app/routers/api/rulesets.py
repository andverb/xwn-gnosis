from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db import get_db
from app.dependencies.auth import verify_api_key

router = APIRouter(prefix="/api/rulesets", tags=["rulesets-api"])


@router.post("/", response_model=schemas.RuleSet, dependencies=[Depends(verify_api_key)])
async def create_ruleset(ruleset: schemas.RuleSetCreate, db: AsyncSession = Depends(get_db)):
    if ruleset.base_ruleset_id is not None:
        stmt = select(models.RuleSet).where(models.RuleSet.id == ruleset.base_ruleset_id)
        result = await db.execute(stmt)
        base_ruleset = result.scalar_one_or_none()
        if base_ruleset is None:
            raise HTTPException(status_code=404, detail="Base RuleSet not found")

    db_ruleset = models.RuleSet(**ruleset.model_dump())
    db.add(db_ruleset)
    await db.commit()
    await db.refresh(db_ruleset)
    return db_ruleset


@router.get("/", response_model=list[schemas.RuleSet])
async def list_rulesets(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    stmt = select(models.RuleSet).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{ruleset_id}", response_model=schemas.RuleSet)
async def get_ruleset(ruleset_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.RuleSet).where(models.RuleSet.id == ruleset_id)
    result = await db.execute(stmt)
    ruleset = result.scalar_one_or_none()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return ruleset


@router.put("/{ruleset_id}", response_model=schemas.RuleSet, dependencies=[Depends(verify_api_key)])
async def update_ruleset(ruleset_id: int, ruleset_update: schemas.RuleSetUpdate, db: AsyncSession = Depends(get_db)):
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

    await db.commit()
    await db.refresh(ruleset)
    return ruleset


@router.delete("/{ruleset_id}", dependencies=[Depends(verify_api_key)])
async def delete_ruleset(ruleset_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.RuleSet).where(models.RuleSet.id == ruleset_id)
    result = await db.execute(stmt)
    ruleset = result.scalar_one_or_none()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")

    await db.delete(ruleset)
    await db.commit()
    return {"message": "Ruleset deleted successfully"}
