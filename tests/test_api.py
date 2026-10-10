
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.is_json


def test_tasks_without_token(client):
    response = client.get("/api/tasks")

    assert response.status_code == 401


def test_profile_without_token(client):
    response = client.get("/api/auth/profile")

    assert response.status_code == 401


def test_unknown_endpoint(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
