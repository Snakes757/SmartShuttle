from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import initialize_firebase
from app.routers import (
    ai_features_router,
    passengers_router,
    routes_router,
    trips_router,
    shuttles_router,
    payments_router
)

origins = [
    "http://localhost",
    "http://localhost:8081", # Default Expo Go port
    "exp://*", # Allow connections from Expo Go
    # Add your production frontend URLs here
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    Initializes Firebase Admin SDK before the app starts accepting requests.
    """
    print("Starting NextRide Solution API...")
    initialize_firebase()
    yield
    print("Shutting down NextRide Solution API...")

app = FastAPI(
    title="NextRide Solution API",
    description="Backend for the E-Shuttle System mapping Routes, Trips, and Passengers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration to allow your React Native / Web frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all endpoint routers defined in Batch 2
app.include_router(passengers_router, prefix="/api/v1")
app.include_router(routes_router, prefix="/api/v1")
app.include_router(trips_router, prefix="/api/v1")
app.include_router(ai_features_router, prefix="/api/v1")
app.include_router(shuttles_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")

@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "status": "online",
        "service": "NextRide E-Shuttle API",
        "version": "1.0.0"
    }