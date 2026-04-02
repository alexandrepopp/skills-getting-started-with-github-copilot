import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app, follow_redirects=False)

@pytest.fixture(autouse=True)
def reset_activities(client):
    """Reset activities to initial state before each test"""
    client.post("/reset")