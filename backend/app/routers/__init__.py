from app.routers.ai_features import router as ai_features_router
from app.routers.passengers import router as passengers_router
from app.routers.routes import router as routes_router
from app.routers.trips import router as trips_router
from app.routers.shuttles import router as shuttles_router
from app.routers.payments import router as payments_router

__all__ = [
    "ai_features_router",
    "passengers_router",
    "routes_router",
    "trips_router",
    "shuttles_router",
    "payments_router"
]