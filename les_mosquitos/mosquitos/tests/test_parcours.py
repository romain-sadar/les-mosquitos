from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from unittest.mock import patch

from ..models import Label, Point, Parcours, ParcoursPoint


class ParcoursTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="tester",
            password="test1234"
        )

        token = Token.objects.create(user=self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        self.label = Label.objects.create(name="Eau")

        self.point = Point.objects.create(
            name="Point 1",
            latitude=48.85,
            longitude=2.35,
            label=self.label,
            created_by=self.user
        )

        self.parcours = Parcours.objects.create(name="Mission")

    def test_add_point(self):
        response = self.client.post(
            f"/api/parcours/{self.parcours.id}/add_point/",
            {"point_id": str(self.point.id)}
        )

        self.assertEqual(response.status_code, 200)

    @patch("les_mosquitos.mosquitos.views.requests.get")
    def test_optimize(self, mock_get):

        point2 = Point.objects.create(
            name="Point 2",
            latitude=48.86,
            longitude=2.36,
            label=self.label,
            created_by=self.user
        )

        ParcoursPoint.objects.create(
            parcours=self.parcours,
            point=self.point,
            visit_order=1
        )

        ParcoursPoint.objects.create(
            parcours=self.parcours,
            point=point2,
            visit_order=2
        )

        mock_get.return_value.json.return_value = {
            "trips": [{
                "distance": 1200,
                "duration": 600,
                "geometry": {"coordinates": []}
            }],
            "waypoints": [
                {"waypoint_index": 0},
                {"waypoint_index": 1}
            ]
        }

        response = self.client.get(
            f"/api/parcours/{self.parcours.id}/optimize/"
        )

        self.assertEqual(response.status_code, 200)