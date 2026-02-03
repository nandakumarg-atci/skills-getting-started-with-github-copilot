import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Test that the endpoint returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Basketball Team" in data

    def test_get_activities_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        email = "test_student@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_duplicate_student(self):
        """Test that a student cannot sign up twice for the same activity"""
        email = "michael@mergington.edu"  # Already signed up
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_activity_not_found(self):
        """Test signup for a non-existent activity"""
        email = "test_student@mergington.edu"
        response = client.post(
            "/activities/Non Existent Activity/signup",
            params={"email": email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds the participant to the activity"""
        email = "new_student@mergington.edu"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Tennis Club"]["participants"])
        
        # Sign up
        client.post("/activities/Tennis Club/signup", params={"email": email})
        
        # Check participant was added
        response = client.get("/activities")
        final_count = len(response.json()["Tennis Club"]["participants"])
        assert final_count == initial_count + 1
        assert email in response.json()["Tennis Club"]["participants"]


class TestUnregisterFromActivity:
    """Test the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        email = "daniel@mergington.edu"  # Already signed up for Chess Club
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_student_not_signed_up(self):
        """Test unregister for a student not signed up"""
        email = "not_signed_up@mergington.edu"
        response = client.post(
            "/activities/Drama Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_activity_not_found(self):
        """Test unregister from a non-existent activity"""
        email = "test_student@mergington.edu"
        response = client.post(
            "/activities/Non Existent Activity/unregister",
            params={"email": email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "lucas@mergington.edu"  # Already signed up for Drama Club
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()["Drama Club"]["participants"])
        
        # Unregister
        client.post("/activities/Drama Club/unregister", params={"email": email})
        
        # Check participant was removed
        response = client.get("/activities")
        final_count = len(response.json()["Drama Club"]["participants"])
        assert final_count == initial_count - 1
        assert email not in response.json()["Drama Club"]["participants"]


class TestRootRoute:
    """Test the root route"""

    def test_root_redirects_to_static(self):
        """Test that root route redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
