import pytest

def test_root_redirect(client):
    """Test root endpoint redirects to static page"""
    # ARRANGE - No special setup needed

    # ACT - Make request to root endpoint
    response = client.get("/")

    # ASSERT - Verify redirect response
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting all activities returns correct structure"""
    # ARRANGE - Activities are already set up in fixture

    # ACT - Request all activities
    response = client.get("/activities")

    # ASSERT - Verify response structure and content
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success(client):
    """Test successful signup adds participant to activity"""
    # ARRANGE - Set up test data
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # ACT - Perform signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # ASSERT - Verify successful response
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for {activity_name}" in data["message"]

    # ASSERT - Verify participant was actually added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate_prevented(client):
    """Test that duplicate signup is prevented"""
    # ARRANGE - Set up initial signup
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # ACT - Attempt duplicate signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # ASSERT - Verify error response
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_activity_full_prevented(client):
    """Test that signup is prevented when activity is at capacity"""
    # ARRANGE - Fill up an activity (Programming Class: max 20, starts with 2)
    activity_name = "Programming Class"
    for i in range(18):  # Fill remaining spots
        client.post(f"/activities/{activity_name}/signup?email=student{i}@mergington.edu")

    # ACT - Attempt signup when full
    response = client.post(f"/activities/{activity_name}/signup?email=laststudent@mergington.edu")

    # ASSERT - Verify error response
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "full" in data["detail"]

def test_signup_nonexistent_activity_fails(client):
    """Test that signup fails for non-existent activity"""
    # ARRANGE - Use invalid activity name
    activity_name = "NonExistent"
    email = "test@mergington.edu"

    # ACT - Attempt signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # ASSERT - Verify error response
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_unregister_success(client):
    """Test successful unregister removes participant from activity"""
    # ARRANGE - Set up participant in activity
    activity_name = "Chess Club"
    email = "removeme@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # ACT - Perform unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # ASSERT - Verify successful response
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from {activity_name}" in data["message"]

    # ASSERT - Verify participant was actually removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_signed_up_fails(client):
    """Test that unregister fails for participant not in activity"""
    # ARRANGE - Use email not in activity
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"

    # ACT - Attempt unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # ASSERT - Verify error response
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_unregister_nonexistent_activity_fails(client):
    """Test that unregister fails for non-existent activity"""
    # ARRANGE - Use invalid activity name
    activity_name = "NonExistent"
    email = "test@mergington.edu"

    # ACT - Attempt unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # ASSERT - Verify error response
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]