import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    # Should redirect to /static/index.html
    assert response.headers.get("location", "").endswith("/static/index.html")

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

def test_signup_for_activity_success():
    response = client.post("/activities/Chess%20Club/signup?email=tester@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "tester@mergington.edu" in data["participants"]

def test_signup_for_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=ghost@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_for_activity_duplicate():
    # First signup
    client.post("/activities/Chess%20Club/signup?email=dupe@mergington.edu")
    # Duplicate signup
    response = client.post("/activities/Chess%20Club/signup?email=dupe@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already registered for this activity"

def test_signup_for_activity_full():
    # Fill up the activity using API calls
    # First, get current participants and max
    resp = client.get("/activities")
    data = resp.json()["Chess Club"]
    max_participants = data["max_participants"]
    current_count = len(data["participants"])
    for i in range(max_participants - current_count):
        client.post(f"/activities/Chess%20Club/signup?email=full{i}@mergington.edu")
    response = client.post("/activities/Chess%20Club/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"

def test_unregister_participant():
    # Register, then unregister
    client.post("/activities/Gym%20Class/signup?email=remove@mergington.edu")
    response = client.post("/activities/Gym%20Class/unregister?email=remove@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "remove@mergington.edu" not in data["participants"]
