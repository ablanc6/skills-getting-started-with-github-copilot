"""Comprehensive tests for the Mergington High School API endpoints."""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_all_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary of activities."""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_expected_fields(self, client):
        """Test that each activity has the expected fields."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_get_activities_contains_chess_club(self, client):
        """Test that Chess Club is in the list of activities."""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities


class TestRootRedirect:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers.get("location", "")


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup to an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "student@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signing up with duplicate email returns 400."""
        email = "duplicate@example.com"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 400

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signup to a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@example.com"}
        )
        assert response.status_code == 404

    def test_signup_adds_participant_to_activity(self, client):
        """Test that a signed-up student appears in activity participants."""
        email = "participant@example.com"
        
        # Signup
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        # Verify participant is in the list
        response = client.get("/activities")
        activities = response.json()
        tennis_club = activities["Tennis Club"]
        assert email in tennis_club["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_successful(self, client):
        """Test successful removal of a participant from an activity."""
        email = "remove_test@example.com"
        
        # First signup
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        
        # Then remove
        response = client.delete(f"/activities/Art Studio/participants/{email}")
        assert response.status_code == 200

    def test_remove_participant_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/participants/test@example.com"
        )
        assert response.status_code == 404

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing non-existent participant returns 404."""
        response = client.delete(
            "/activities/Music Performance/participants/nonexistent@example.com"
        )
        assert response.status_code == 404

    def test_remove_participant_removes_from_list(self, client):
        """Test that a removed participant no longer appears in the activity."""
        email = "remove_verify@example.com"
        activity = "Debate Team"
        
        # Signup
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify in list
        response = client.get("/activities")
        activities = response.json()
        activity_data = activities[activity]
        assert email in activity_data["participants"]
        
        # Remove
        client.delete(f"/activities/{activity}/participants/{email}")
        
        # Verify removed from list
        response = client.get("/activities")
        activities = response.json()
        activity_data = activities[activity]
        assert email not in activity_data["participants"]
