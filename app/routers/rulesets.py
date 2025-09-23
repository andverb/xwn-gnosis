from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.dependencies.auth import verify_api_key

router = APIRouter(prefix="/rulesets", tags=["rulesets"])


@router.post("/", response_model=schemas.RuleSet, dependencies=[Depends(verify_api_key)])
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


@router.get("/", response_model=list[schemas.RuleSet])
def list_rulesets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.RuleSet).offset(skip).limit(limit).all()


@router.get("/{ruleset_id}", response_model=schemas.RuleSet)
def get_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == ruleset_id).first()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    return ruleset


@router.put("/{ruleset_id}", response_model=schemas.RuleSet, dependencies=[Depends(verify_api_key)])
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


@router.delete("/{ruleset_id}", dependencies=[Depends(verify_api_key)])
def delete_ruleset(ruleset_id: int, db: Session = Depends(get_db)):
    ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == ruleset_id).first()
    if ruleset is None:
        raise HTTPException(status_code=404, detail="Ruleset not found")

    db.delete(ruleset)
    db.commit()
    return {"message": "Ruleset deleted successfully"}
