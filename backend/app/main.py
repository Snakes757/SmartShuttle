import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="NextRide Solution API",
    description="Backend for the E-Shuttle System",
    version="1.0.0"
)

origins = [
    "http://localhost",
    "http://localhost:8081", # Default Expo Go port
    "exp://*", # Allow connections from Expo Go
    # Add your production frontend URLs here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, etc.)
    allow_headers=["*"], # Allows all headers
)


@app.get("/", tags=["Root"])
async def read_root():
    return {
        "status": "online",
        "service": "NextRide E-Shuttle API",
        "version": "1.0.0"
    }
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )