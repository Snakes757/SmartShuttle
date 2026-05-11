from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from app.schemas import TripCreate, TripResponse, PickUpPointCreate, FareCalculationRequest, FareResponse
from app.dependencies import get_current_user
from app.services.fare_strategy import FareCalculatorContext, StandardTripStrategy, PeakHourStrategy
from app.services.ai_service import estimate_tolls_for_route
import uuid
from datetime import datetime

router = APIRouter(prefix="/trips", tags=["Trips & Booking"])

@router.post("/calculate-fare", response_model=FareResponse)
async def calculate_trip_fare(request: FareCalculationRequest, current_user: dict = Depends(get_current_user)):
    """
    Calculates the fare using AI Toll Extraction and the Strategy Pattern 
    BEFORE the passenger actually books the seat.
    """
    db = firestore.client()
    route_doc = db.collection("routes").document(request.route_id).get()
    
    if not route_doc.exists:
        raise HTTPException(status_code=404, detail="Route not found")
        
    route_data = route_doc.to_dict()
    distance_km = route_data.get("base_distance_km", 0)
    
    # 1. AI Integration: Get Tolls
    tolls_zar = await estimate_tolls_for_route(route_data["point_a_start"], route_data["point_b_end"])
    
    # 2. Strategy Pattern Selection (Dynamic pricing based on runtime conditions)
    hour = request.trip_time.hour
    is_peak_hour = (6 <= hour <= 9) or (15 <= hour <= 18) # Example Peak Hours
    
    if is_peak_hour:
        calculator = FareCalculatorContext(PeakHourStrategy())
    else:
        calculator = FareCalculatorContext(StandardTripStrategy())
        
    # Standard fuel rate assumption (e.g., R2.50 per km)
    fuel_rate = 2.50 
    
    # 3. Calculate Fare
    fare_details = calculator.calculate(distance=distance_km, fuel=fuel_rate, tolls=tolls_zar, pax=request.passengers_count)
    
    return FareResponse(
        base_fare=fare_details["base_cost"],
        tolls=fare_details["tolls"],
        commission=fare_details["commission"],
        total_cost=fare_details["total_fare"],
        cost_per_passenger=fare_details["per_passenger"],
        strategy_applied=fare_details["strategy_applied"]
    )

@router.post("/book", response_model=TripResponse)
async def book_trip(trip: TripCreate, current_user: dict = Depends(get_current_user)):
    """Books the actual trip after the passenger has seen and accepted the fare."""
    db = firestore.client()
    trip_id = str(uuid.uuid4())
    trip_data = trip.model_dump()
    trip_data["departure_time"] = trip_data["departure_time"].isoformat()
    trip_data["id"] = trip_id
    trip_data["passenger_id"] = current_user["uid"]
    
    try:
        db.collection("trips").document(trip_id).set(trip_data)
        return trip_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")