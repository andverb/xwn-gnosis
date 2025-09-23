from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.dependencies.auth import verify_api_key

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("/", response_model=schemas.Rule, dependencies=[Depends(verify_api_key)])
def create_rule(rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    # Validate required ruleset_id
    ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == rule.ruleset_id).first()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="RuleSet not found")

    # Validate optional base_rule_id
    if rule.base_rule_id is not None:
        base_rule = db.query(models.Rule).filter(models.Rule.id == rule.base_rule_id).first()
        if base_rule is None:
            raise HTTPException(status_code=404, detail="Base Rule not found")

    db_rule = models.Rule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("/", response_model=list[schemas.Rule])
def list_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Rule).offset(skip).limit(limit).all()


@router.get("/{rule_id}", response_model=schemas.Rule)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=schemas.Rule, dependencies=[Depends(verify_api_key)])
def update_rule(rule_id: int, rule_update: schemas.RuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = rule_update.model_dump(exclude_unset=True)
    # FK validation if ruleset_id is being updated
    if "ruleset_id" in update_data:
        ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == update_data["ruleset_id"]).first()
        if ruleset is None:
            raise HTTPException(status_code=404, detail="RuleSet not found")

    for field, value in update_data.items():
        setattr(rule, field, value)

    # TODO proper user implementation. Model populates only at creation
    rule.last_update_by = "sorcerer-king-admin"

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", dependencies=[Depends(verify_api_key)])
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}
