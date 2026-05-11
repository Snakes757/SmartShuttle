import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.dependencies import get_current_user

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_auth_dependency():
    app.dependency_overrides[get_current_user] = lambda: {"uid": "mock_passenger_uid", "email": "mock@test.com"}
    yield
    app.dependency_overrides.clear()

@patch("app.routers.passengers.firestore.client")
def test_create_passenger_success(mock_firestore_client):
    # Mock Firestore setup
    mock_db = MagicMock()
    mock_firestore_client.return_value = mock_db
    mock_doc = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc

    payload = {
        "full_name": "John Doe",
        "gender": "Male",
        "id_number": "9001015000000",
        "age": 30,
        "email": "john.doe@test.com",
        "phone_number": "+27123456789",
        "password": "securepassword123",
        "parent_id": None
    }

    response = client.post("/api/v1/passengers/", json=payload)

    assert response.status_code == 200
    data = response.json()
    
    assert data["full_name"] == "John Doe"
    assert data["is_verified"] is False
    assert data["id"] == "mock_passenger_uid" # ID should map to the auth uid
    assert "password" not in data  # Ensure sensitive data is not returned to client
    
    # Check that it attempted to save to DB
    mock_doc.set.assert_called_once()

@patch("app.routers.passengers.firestore.client")
def test_create_passenger_underage_without_parent(mock_firestore_client):
    payload = {
        "full_name": "Jane Doe",
        "gender": "Female",
        "id_number": "1001015000000",
        "age": 16, # Underage
        "email": "jane.doe@test.com",
        "phone_number": "+27123456789",
        "password": "securepassword123",
        "parent_id": None # No parent provided
    }

    response = client.post("/api/v1/passengers/", json=payload)

    # Expecting 400 Bad Request because age < 18 requires parent_id
    assert response.status_code == 400
    assert "parent_id required" in response.json()["detail"]

@patch("app.routers.passengers.firestore.client")
def test_verify_passenger_success(mock_firestore_client):
    mock_db = MagicMock()
    mock_firestore_client.return_value = mock_db
    mock_doc = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc

    # Our hardcoded mock code is 123456
    response = client.post("/api/v1/passengers/test_passenger_id/verify?code=123456")

    assert response.status_code == 200
    assert response.json()["message"] == "Passenger successfully verified"
    
    # Check that verification update happened
    mock_doc.update.assert_called_once_with({"is_verified": True})

def test_verify_passenger_invalid_code():
    # Sending wrong verification code
    response = client.post("/api/v1/passengers/test_passenger_id/verify?code=999999")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid verification code"