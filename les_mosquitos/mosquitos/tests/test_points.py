from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

from ..models import Label, Point


class PointTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username="tester", password="test1234")

        token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        self.label = Label.objects.create(name="Eau stagnante", is_treatable=True)

        self.point = Point.objects.create(
            name="Point 1",
            latitude=48.85,
            longitude=2.35,
            label=self.label,
            created_by=self.user,
        )

    def test_create_point(self):
        response = self.client.post(
            "/api/points/",
            {
                "name": "Point 2",
                "latitude": 48.86,
                "longitude": 2.36,
                "label_id": str(self.label.id),
            },
        )

        self.assertEqual(response.status_code, 201)

    def test_mark_treated(self):
        response = self.client.post(f"/api/points/{self.point.id}/mark_treated/")

        self.assertEqual(response.status_code, 200)

    def test_treatment_expiration(self):
        self.point.is_treated = True
        self.point.last_treatment_date = timezone.now() - timedelta(weeks=7)
        self.point.save()

        self.point.check_treatment_status()
        self.point.refresh_from_db()

        self.assertFalse(self.point.is_treated)
