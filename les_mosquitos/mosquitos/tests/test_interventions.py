import pytest

pytestmark = pytest.mark.django_db


def test_create_intervention(auth_client, point):
    client, _ = auth_client

    response = client.post(
        "/api/interventions/",
        {"point_id": str(point.id), "intervention_type": "treated"},
    )

    assert response.status_code == 201
