from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore
from app.dependencies import get_current_user
from app.schemas import PaymentMethod
from datetime import datetime, timedelta, timezone
import uuid

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/initiate")
async def initiate_payment(
    trip_id: str, 
    method: PaymentMethod, 
    amount: float,
    current_user: dict = Depends(get_current_user)
):
    """
    Initiates the payment. If CARD, sets a strict 2-minute expiry window for banking app verification.
    """
    db = firestore.client()
    payment_id = str(uuid.uuid4())
    
    payment_data = {
        "id": payment_id,
        "trip_id": trip_id,
        "passenger_id": current_user["uid"],
        "amount": amount,
        "method": method.value,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    if method == PaymentMethod.CARD:
        # Enforce 2-minute time limit for Card Gateway
        expiry_time = datetime.now(timezone.utc) + timedelta(minutes=2)
        payment_data["expires_at"] = expiry_time.isoformat()
        payment_data["gateway_message"] = "Please verify payment in your banking app within 2 minutes."
    
    db.collection("payments").document(payment_id).set(payment_data)
    return payment_data

@router.post("/{payment_id}/verify")
async def verify_payment(payment_id: str, current_user: dict = Depends(get_current_user)):
    """Checks if the payment was verified within the 2-minute window."""
    db = firestore.client()
    doc_ref = db.collection("payments").document(payment_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Payment record not found")
        
    payment_data = doc.to_dict()
    
    if payment_data["status"] != "PENDING":
        return {"status": payment_data["status"], "message": "Payment already processed."}
        
    if payment_data["method"] == PaymentMethod.CARD.value:
        # Check 2-minute expiration logic
        expires_at = datetime.fromisoformat(payment_data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            doc_ref.update({"status": "FAILED_TIMEOUT"})
            raise HTTPException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT, 
                detail="Payment Gateway Timeout: 2 minutes have passed. Please restart payment."
            )
            
    # If within time (or if it's Cash), mark as success
    doc_ref.update({"status": "SUCCESS"})
    return {"status": "SUCCESS", "message": "Payment verified successfully."}