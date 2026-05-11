from fastapi import Depends
from app.core.security import verify_firebase_token

def get_current_user(decoded_token: dict = Depends(verify_firebase_token)) -> dict:
    """
    FastAPI dependency to extract the current authenticated user's information.
    Usage in router endpoints:
    async def my_endpoint(user: dict = Depends(get_current_user)):
        user_id = user["uid"]
    """
    return decoded_token