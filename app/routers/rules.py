from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db import get_db
from app.dependencies.auth import verify_api_key

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/", response_model=schemas.Rule, dependencies=[Depends(verify_api_key)])
async def create_rule(rule: schemas.RuleCreate, db: AsyncSession = Depends(get_db)):
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
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.get("/", response_model=list[schemas.Rule])
async def list_rules(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Rule).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{rule_id}", response_model=schemas.Rule)
async def get_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Rule).where(models.Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=schemas.Rule, dependencies=[Depends(verify_api_key)])
async def update_rule(rule_id: int, rule_update: schemas.RuleUpdate, db: AsyncSession = Depends(get_db)):
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


@router.delete("/{rule_id}", dependencies=[Depends(verify_api_key)])
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.Rule).where(models.Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    await db.delete(rule)
    await db.commit()
    return {"message": "Rule deleted successfully"}
