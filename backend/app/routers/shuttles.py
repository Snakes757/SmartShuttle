from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore
from app.schemas import ShuttleOwnerCreate, ShuttleOwnerResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/shuttles", tags=["Shuttles & Drivers"])

@router.post("/register", response_model=ShuttleOwnerResponse)
async def register_shuttle_owner(
    owner: ShuttleOwnerCreate, 
    current_user: dict = Depends(get_current_user)
):
    """
    Registers a shuttle owner and their vehicle. 
    Enforces business rules (e.g., 7-seaters must have a trailer).
    """
    # Business Rule Enforcement
    if owner.vehicle.capacity == 7 and not owner.vehicle.has_trailer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Vehicles with 7 seats must have a trailer registered for luggage."
        )

    db = firestore.client()
    owner_data = owner.model_dump(exclude={"password"})
    owner_data["id"] = current_user["uid"]
    
    try:
        # Save to real-time database equivalent/Firestore
        db.collection("shuttle_owners").document(current_user["uid"]).set(owner_data)
        return owner_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register owner: {str(e)}")