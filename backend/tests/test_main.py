"""
Basic tests for the Agent Mark backend
"""

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Agent Mark API" in data["message"]

def test_models_endpoint_without_auth():
    """Test that models endpoint requires authentication"""
    response = client.get("/models/")
    assert response.status_code == 403  # Should require authentication
