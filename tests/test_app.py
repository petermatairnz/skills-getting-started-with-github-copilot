import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    """Create a test client for our app"""
    return TestClient(app)

@pytest.fixture
def sample_activity():
    """Return a sample activity data structure"""
    return {
        "description": "Test Activity",
        "schedule": "Monday, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    }

def test_root_redirect(client):
    """Test that the root endpoint redirects to the static index.html"""
    response = client.get("/")
    assert response.status_code == 200  # Permanent redirect via RedirectResponse
    assert response.url.path == "/static/index.html"  # Check the final URL after redirect

def test_get_activities(client):
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    # Check that we have some activities
    assert len(activities) > 0
    # Check the structure of an activity
    activity = list(activities.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_for_activity(client):
    """Test signing up for an activity"""
    # Get the first activity name
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # Test successful signup
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate(client):
    """Test signing up the same student twice"""
    # Get the first activity name
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # Sign up once
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Try to sign up again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post("/activities/NonexistentActivity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity(client):
    """Test unregistering from an activity"""
    # Get the first activity name
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    # First sign up a student
    email = "unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Now unregister them
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered(client):
    """Test unregistering a student who isn't registered"""
    # Get the first activity name
    activities = client.get("/activities").json()
    activity_name = list(activities.keys())[0]
    
    response = client.post(f"/activities/{activity_name}/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.post("/activities/NonexistentActivity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()