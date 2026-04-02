from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from ..models import Parcours


class TrackTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username="tester", password="test1234")

        token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        self.parcours = Parcours.objects.create(name="Mission")

    def test_create_track(self):
        response = self.client.post(
            "/api/mission-tracks/",
            {"parcours": str(self.parcours.id), "latitude": 48.85, "longitude": 2.35},
        )

        self.assertEqual(response.status_code, 201)
