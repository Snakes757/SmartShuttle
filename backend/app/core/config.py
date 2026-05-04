import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore import Client
from google.oauth2 import service_account
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    API_PORT: int = int(os.getenv("PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
db: Optional[Client] = None

try:
    if settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
        try:
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
    # This will raise an exception if auth is used without initialization, which is correct.
    return auth