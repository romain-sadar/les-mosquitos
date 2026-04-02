from unittest.mock import patch
from les_mosquitos.mosquitos.models import ParcoursPoint, Point


def test_add_point(auth_client, point, parcours):
    client, _ = auth_client

    response = client.post(
        f"/api/parcours/{parcours.id}/add_point/", {"point_id": str(point.id)}
    )

    assert response.status_code == 200


@patch("les_mosquitos.mosquitos.views.requests.get")
def test_optimize(mock_get, auth_client, point, parcours):

    _, user = auth_client

    point2 = Point.objects.create(
        name="Point 2",
        latitude=48.857,
        longitude=2.353,
        label=point.label,
        created_by=user,
    )

    ParcoursPoint.objects.create(parcours=parcours, point=point, visit_order=1)

    ParcoursPoint.objects.create(parcours=parcours, point=point2, visit_order=2)

    mock_get.return_value.json.return_value = {
        "trips": [{"distance": 1200, "duration": 600, "geometry": {"coordinates": []}}],
        "waypoints": [{"waypoint_index": 0}, {"waypoint_index": 1}],
    }

    response = auth_client[0].get(f"/api/parcours/{parcours.id}/optimize/")

    assert response.status_code == 200
