import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.dependencies import get_current_user

# Initialize the test client
client = TestClient(app)

# --- MOCK DEPENDENCIES ---
def override_get_current_user():
    """Mock the authenticated user to bypass Firebase Auth during testing."""
    return {"uid": "mock_test_user_123", "email": "test@passenger.com"}

# Apply the override to the FastAPI app
app.dependency_overrides[get_current_user] = override_get_current_user


# --- TEST CASES ---
@pytest.fixture(autouse=True)
def override_auth_dependency():
    app.dependency_overrides[get_current_user] = lambda: {"uid": "mock_test_user_123", "email": "test@passenger.com"}
    yield
    app.dependency_overrides.clear()

@patch("app.routers.routes.firestore.client")
def test_create_route_success(mock_firestore_client):
# ... existing code ...
    """
    Test Case: Creating a new route successfully.
    Acceptance Criteria: Given a valid payload, the system assigns a UUID and saves it to Firestore.
    """
    # 1. Setup the mock database response
    mock_db = MagicMock()
    mock_firestore_client.return_value = mock_db
    
    # Mock the collection chaining: db.collection("routes").document(route_id).set(route_data)
    mock_document = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_document

    # 2. Define the payload (Based on RouteCreate schema)
    payload = {
        "name": "Pretoria to Johannesburg",
        "point_a_start": "Pretoria CBD",
        "point_b_end": "Johannesburg Park Station",
        "base_distance_km": 60.5
    }

    # 3. Execute the request
    # Note: prefix in main.py usually wraps this as /api/v1/routes/
    # If not prefixed in testing, use the router prefix directly
    response = client.post("/api/v1/routes/", json=payload)

    # 4. Assertions
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Pretoria to Johannesburg"
    assert "id" in data  # Ensure UUID was generated
    
    # Verify the mock database was actually called to save the data
    mock_db.collection.assert_called_with("routes")
    mock_document.set.assert_called_once()


@patch("app.routers.routes.firestore.client")
def test_create_route_database_error(mock_firestore_client):
    """
    Test Case: Handle Database Failure.
    Acceptance Criteria: If Firestore fails, the system safely catches it and returns a 500 error.
    """
    # 1. Setup the mock to raise an exception when .set() is called
    mock_db = MagicMock()
    mock_firestore_client.return_value = mock_db
    mock_db.collection.return_value.document.return_value.set.side_effect = Exception("Firebase Timeout")

    payload = {
        "name": "Test Route",
        "point_a_start": "A",
        "point_b_end": "B",
        "base_distance_km": 10.0
    }

    # 2. Execute
    response = client.post("/api/v1/routes/", json=payload)

    # 3. Assertions
    assert response.status_code == 500
    assert "Failed to create route" in response.json()["detail"]


@patch("app.routers.routes.firestore.client")
def test_list_routes_success(mock_firestore_client):
    """
    Test Case: Retrieve all routes.
    Acceptance Criteria: The system correctly maps the Firestore stream into a list of RouteResponses.
    """
    # 1. Setup mock to return a simulated list of documents
    mock_db = MagicMock()
    mock_firestore_client.return_value = mock_db
    
    # Create mock documents with a .to_dict() method
    mock_doc_1 = MagicMock()
    mock_doc_1.to_dict.return_value = {
        "id": "uuid-1",
        "name": "Route 1",
        "point_a_start": "Location A",
        "point_b_end": "Location B",
        "base_distance_km": 15.0
    }
    
    mock_doc_2 = MagicMock()
    mock_doc_2.to_dict.return_value = {
        "id": "uuid-2",
        "name": "Route 2",
        "point_a_start": "Location C",
        "point_b_end": "Location D",
        "base_distance_km": 20.0
    }
    
    # Attach documents to the .stream() mock
    mock_db.collection.return_value.stream.return_value = [mock_doc_1, mock_doc_2]

    # 2. Execute
    response = client.get("/api/v1/routes/")

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Route 1"
    assert data[1]["id"] == "uuid-2"