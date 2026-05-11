from fastapi import APIRouter, Depends, HTTPException
from app.schemas import PickUpPointCreate, RouteBase
from app.services.ai_service import evaluate_detour_viability
from app.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Features"])

@router.post("/predict-detour")
async def predict_detour(
    pickup: PickUpPointCreate,
    route: RouteBase,
    current_user: dict = Depends(get_current_user)
):
    """
    Uses Gemini AI to evaluate if a passenger's requested pick-up point 
    (e.g., 'Tau') affects the route heavily based on the radius rule.
    """
    try:
        evaluation = await evaluate_detour_viability(pickup, route)
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))