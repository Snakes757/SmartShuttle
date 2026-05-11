import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore import Client
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    API_PORT: int = int(os.getenv("PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")

    # Replaced deprecated 'class Config:' with Pydantic V2 model_config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
db: Optional[Client] = None

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK. 
    Called by the FastAPI lifespan manager in main.py.
    """
    global db
    try:
        if settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH:
            cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
            try:
                # Check if already initialized to prevent errors during testing/reloads
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app(cred)

            db = firestore.client()
        else:
            print("Warning: FIREBASE_SERVICE_ACCOUNT_KEY_PATH is not set. Firebase Admin SDK not initialized.")

    except FileNotFoundError:
        print(f"Error: Firebase service account key file not found at path: {settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH}")
        db = None
    except Exception as e:
        print(f"An unexpected error occurred during Firebase initialization: {e}")
        db = None

def get_db() -> Client:
    if db is None:
        raise RuntimeError("Firestore database client is not initialized.")
    return db

def get_auth():
    return auth