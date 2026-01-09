"""Test health check endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint returns correct status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Sweets EC API"
    assert "version" in data
    assert "environment" in data


def test_health_check_includes_correlation_id():
    """Test health check includes correlation ID in response header."""
    response = client.get("/health")
    assert "X-Correlation-ID" in response.headers
    assert len(response.headers["X-Correlation-ID"]) > 0


def test_root_endpoint():
    """Test root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "correlation_id" in data


def test_correlation_id_preserved():
    """Test custom correlation ID is preserved."""
    custom_id = "test-correlation-123"
    response = client.get("/health", headers={"X-Correlation-ID": custom_id})
    assert response.headers["X-Correlation-ID"] == custom_id
