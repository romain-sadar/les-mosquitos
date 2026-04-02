from django.utils import timezone
from datetime import timedelta
from les_mosquitos.mosquitos.models import Point
import pytest

pytestmark = pytest.mark.django_db


def test_create_point(auth_client, label):
    client, _ = auth_client

    response = client.post(
        "/api/points/",
        {
            "name": "Nouveau point",
            "latitude": 48.85,
            "longitude": 2.35,
            "label_id": str(label.id),
        },
    )

    assert response.status_code == 201


def test_mark_treated(auth_client, point):
    client, _ = auth_client

    response = client.post(f"/api/points/{point.id}/mark_treated/")

    assert response.status_code == 200


def test_non_treatable_forces_false(non_treatable_label, auth_client):
    _, user = auth_client

    point = Point.objects.create(
        name="Sec",
        latitude=48.8,
        longitude=2.3,
        label=non_treatable_label,
        is_treated=True,
        created_by=user,
    )

    assert point.is_treated is False


def test_treatment_expiration(point):
    point.is_treated = True
    point.last_treatment_date = timezone.now() - timedelta(weeks=7)
    point.save()

    point.check_treatment_status()
    point.refresh_from_db()

    assert point.is_treated is False
