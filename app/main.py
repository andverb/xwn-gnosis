from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Rule as RuleModel
from app.schemas import Rule, RuleCreate, RuleUpdate

app = FastAPI(title="Gnosis - database of rules for xWN family of TRPG systems", version="0.1.0")


@app.get("/")
def health_check():
    return {"message": "Im OK!"}


@app.post("/rules/", response_model=Rule)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    db_rule = RuleModel(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@app.get("/rules/", response_model=list[Rule])
def list_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(RuleModel).offset(skip).limit(limit).all()


@app.get("/rules/{rule_id}", response_model=Rule)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(RuleModel).filter(RuleModel.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@app.put("/rules/{rule_id}", response_model=Rule)
def update_rule(rule_id: int, rule_update: RuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(RuleModel).filter(RuleModel.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(RuleModel).filter(RuleModel.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}
