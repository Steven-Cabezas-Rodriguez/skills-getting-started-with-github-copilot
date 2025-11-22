from fastapi.testclient import TestClient
from urllib.parse import quote
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "pytest_user_test@example.com"

    # Ensure email not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email not in participants

    # Sign up the user
    signup_path = f"/activities/{quote(activity)}/signup"
    resp = client.post(signup_path, params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email} for {activity}" in resp.json().get("message", "")

    # Verify user is now present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # Duplicate signup should fail (400)
    resp = client.post(signup_path, params={"email": email})
    assert resp.status_code == 400

    # Unregister the user
    delete_path = f"/activities/{quote(activity)}/participants"
    resp = client.delete(delete_path, params={"email": email})
    assert resp.status_code == 200
    assert f"Unregistered {email} from {activity}" in resp.json().get("message", "")

    # Verify user removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_invalid_activity_signup_and_delete():
    bad_activity = "Nonexistent Club"
    email = "someone@example.com"

    signup_path = f"/activities/{quote(bad_activity)}/signup"
    resp = client.post(signup_path, params={"email": email})
    assert resp.status_code == 404

    delete_path = f"/activities/{quote(bad_activity)}/participants"
    resp = client.delete(delete_path, params={"email": email})
    assert resp.status_code == 404
