import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app import app
from backend.config import env_settings

# Make sure we don't try to load actual credentials in tests
env_settings.environment = "test"

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "scheduler_status" in data

def test_settings_endpoint():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "ai_model" in data

    update_response = client.put("/api/settings", json={"ai_model": "test-model"})
    assert update_response.status_code == 200
    assert update_response.json()["settings"]["ai_model"] == "test-model"

@patch('backend.routers.api.BackgroundTasks.add_task')
def test_run_endpoint(mock_add_task):
    response = client.post("/api/run")
    assert response.status_code == 200
    assert response.json()["status"] == "started"
    mock_add_task.assert_called_once()
