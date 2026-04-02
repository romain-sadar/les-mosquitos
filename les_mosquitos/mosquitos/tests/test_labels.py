from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from ..models import Label


class LabelTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username="tester", password="test1234")

        token = Token.objects.create(user=self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_create_label(self):
        response = self.client.post(
            "/api/labels/",
            {"name": "Déchets", "color": "#0000FF", "is_treatable": True},
        )

        self.assertEqual(response.status_code, 201)

    def test_label_created(self):
        Label.objects.create(name="Eau", is_treatable=True)
        self.assertEqual(Label.objects.count(), 1)
