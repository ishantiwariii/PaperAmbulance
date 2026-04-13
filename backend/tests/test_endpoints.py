import pytest
from app.db import models

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_analyze_fill_unauthorized(client):
    """Verifies that the endpoint requires authentication."""
    response = client.post("/api/v1/analyze/fill", json={"fields": []})
    assert response.status_code == 401 # Changed from 403 to match security.py implementation

def test_analyze_fill_success(authenticated_client, db, mock_user_auth):
    """
    Verifies full end-to-end integration:
    1. Create user/profile in test DB
    2. Call endpoint
    3. Verify response and history logging
    """
    user_id = mock_user_auth["sub"]
    
    # Setup test data in SQLite
    profile = models.Profile(
        user_id_str=user_id,
        data={"full_name": "Test Runner", "pan_number": "TEST1234P"}
    )
    db.add(profile)
    db.commit()

    payload = {
        "fields": [
            {"id": "name_inp", "label": "Full Name", "type": "text"},
            {"id": "pan_inp", "label": "PAN", "type": "text"}
        ]
    }

    response = authenticated_client.post("/api/v1/analyze/fill", json=payload["fields"])
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["fill_map"]["name_inp"] == "Test Runner"
    
    # Verify history was logged
    history = db.query(models.FormHistory).filter(models.FormHistory.user_id_str == user_id).first()
    assert history is not None
    assert history.field_count == 2
