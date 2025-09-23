from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

tags_metadata = [
    {
        "name": "rules",
        "description": "Operations with rules. Individual game mechanics and content.",
    },
    {
        "name": "rulesets",
        "description": "Operations with rulesets. Collections of rules for different game systems.",
    },
]


app = FastAPI(
    title="Gnosis - database of rules for xWN family of TRPG systems", version="0.1.0", openapi_tags=tags_metadata
)


@app.get("/")
def health_check():
    return {"message": "Im OK!"}


@app.post("/rules/", response_model=schemas.Rule, tags=["rules"])
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


@app.get("/rules/", response_model=list[schemas.Rule], tags=["rules"])
def list_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Rule).offset(skip).limit(limit).all()


@app.get("/rules/{rule_id}", response_model=schemas.Rule, tags=["rules"])
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@app.put("/rules/{rule_id}", response_model=schemas.Rule, tags=["rules"])
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


@app.delete("/rules/{rule_id}", tags=["rules"])
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}


# Ruleset routes


@app.post("/rulesets/", response_model=schemas.RuleSet, tags=["rulesets"])
def create_ruleset(ruleset: schemas.RuleSetCreate, db: Session = Depends(get_db)):
    if ruleset.base_ruleset_id is not None:
        base_ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == ruleset.base_ruleset_id).first()
        if base_ruleset is None:
            raise HTTPException(status_code=404, detail="Base RuleSet not found")

    db_ruleset = models.RuleSet(**ruleset.model_dump())
    db.add(db_ruleset)
    db.commit()
    db.refresh(db_ruleset)
    return db_ruleset


@app.get("/rulesets/", response_model=list[schemas.RuleSet], tags=["rulesets"])
def list_rulesets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.RuleSet).offset(skip).limit(limit).all()


@app.get("/rulesets/{ruleset_id}", response_model=schemas.RuleSet, tags=["rulesets"])
def get_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == ruleset_id).first()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return ruleset


@app.put("/rulesets/{ruleset_id}", response_model=schemas.RuleSet, tags=["rulesets"])
def update_ruleset(ruleset_id: int, ruleset_update: schemas.RuleSetUpdate, db: Session = Depends(get_db)):
    ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == ruleset_id).first()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")

    update_data = ruleset_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(ruleset, field, value)

    # FK validation if ruleset_id is being updated
    if "base_ruleset_id" in update_data:
        base_ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == update_data["base_ruleset_id"]).first()
        if base_ruleset is None:
            raise HTTPException(status_code=404, detail="Base RuleSet not found")

    # TODO proper user implementation. Model populates only at creation
    ruleset.last_update_by = "sorcerer-king-admin"

    db.commit()
    db.refresh(ruleset)
    return ruleset


@app.delete("/rulesets/{ruleset_id}", tags=["rulesets"])
def delete_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == ruleset_id).first()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")

    db.delete(ruleset)
    db.commit()
    return {"message": "Ruleset deleted successfully"}
