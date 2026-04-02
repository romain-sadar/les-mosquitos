from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from ..models import Label, Point


class InterventionTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username="tester", password="test1234")

        token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        label = Label.objects.create(name="Eau")

        self.point = Point.objects.create(
            name="Point",
            latitude=48.85,
            longitude=2.35,
            label=label,
            created_by=self.user,
        )

    def test_create_intervention(self):
        response = self.client.post(
            "/api/interventions/",
            {"point_id": str(self.point.id), "intervention_type": "treated"},
        )

        self.assertEqual(response.status_code, 201)
