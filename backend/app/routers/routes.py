from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from app.schemas import RouteCreate, RouteResponse
from app.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/routes", tags=["Routes"])

@router.post("/", response_model=RouteResponse)
async def create_route(route: RouteCreate, current_user: dict = Depends(get_current_user)):
    """
    Creates a baseline route (Point A to Point B).
    """
    db = firestore.client()
    route_id = str(uuid.uuid4())
    
    route_data = route.model_dump()
    route_data["id"] = route_id
    
    try:
        db.collection("routes").document(route_id).set(route_data)
        return route_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create route: {str(e)}")

@router.get("/", response_model=list[RouteResponse])
async def list_routes(current_user: dict = Depends(get_current_user)):
    """Retrieves all available routes in the system."""
    db = firestore.client()
    try:
        routes_query = db.collection("routes").stream()
        return [doc.to_dict() for doc in routes_query]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch routes: {str(e)}")