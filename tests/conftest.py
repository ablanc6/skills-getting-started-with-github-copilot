"""Pytest configuration and shared fixtures for FastAPI tests."""
import pytest
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for testing the FastAPI application."""
    return TestClient(app)
