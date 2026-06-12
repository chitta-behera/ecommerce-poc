import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.repositories.in_memory import storage


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage_before_each_test():
    """
    Fixture to clear the in-memory storage before each test.
    This ensures test isolation.
    """
    storage.clear()
    # Re-initialize with dummy data if needed by tests,
    # or have tests set up their own specific data.
    yield
    storage.clear()
