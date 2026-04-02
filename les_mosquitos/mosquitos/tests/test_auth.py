import pytest

pytestmark = pytest.mark.django_db


def test_register(api_client):
    response = api_client.post(
        "/api/register/", {"username": "newuser", "password": "password123"}
    )

    assert response.status_code == 201


def test_login(api_client):
    api_client.post("/api/register/", {"username": "user1", "password": "password123"})

    response = api_client.post(
        "/api/login/", {"username": "user1", "password": "password123"}
    )

    assert response.status_code == 200
    assert "token" in response.data
