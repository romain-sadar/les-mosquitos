import pytest

pytestmark = pytest.mark.django_db


def test_create_label(auth_client):
    client, _ = auth_client

    response = client.post(
        "/api/labels/", {"name": "Déchets", "color": "#0000FF", "is_treatable": True}
    )

    assert response.status_code == 201
