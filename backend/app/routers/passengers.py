from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore
from app.schemas import PassengerCreate, PassengerResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/passengers", tags=["Passengers"])

@router.post("/", response_model=PassengerResponse)
async def create_passenger_profile(
    passenger: PassengerCreate, 
    current_user: dict = Depends(get_current_user)
):
    """
    Creates a passenger profile.
    Enforces parental consent rules if the passenger is under 18.
    """
    # Business Rule: Under 18 requires parental supervision
    if passenger.age < 18 and not passenger.parent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passengers under 18 must be linked to a registered parent account (parent_id required)."
        )

    db = firestore.client()
    passenger_data = passenger.model_dump(exclude={"password"})
    passenger_data["id"] = current_user["uid"]
    
    # Mock SMS/Email verification step triggering here...
    # In production, this would integrate with Twilio or Firebase Email Verification
    passenger_data["is_verified"] = False 
    
    try:
        doc_ref = db.collection("passengers").document(current_user["uid"])
        doc_ref.set(passenger_data)
        return passenger_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create passenger: {str(e)}")

@router.post("/{passenger_id}/verify")
async def verify_passenger(passenger_id: str, code: str, current_user: dict = Depends(get_current_user)):
    """Mock endpoint for SMS/Email verification completion."""
    if code != "123456": # Mock validation
        raise HTTPException(status_code=400, detail="Invalid verification code")
        
    db = firestore.client()
    db.collection("passengers").document(passenger_id).update({"is_verified": True})
    return {"message": "Passenger successfully verified"}