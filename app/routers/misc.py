from fastapi import APIRouter

router = APIRouter(tags=["utility"])


@router.get("/health")
async def health_check():
    return {"message": "Im OK!"}
