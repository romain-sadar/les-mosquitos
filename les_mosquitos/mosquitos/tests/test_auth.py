from django.test import TestCase
from rest_framework.test import APIClient


class AuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        response = self.client.post(
            "/api/register/", {"username": "newuser", "password": "password123"}
        )

        self.assertEqual(response.status_code, 201)

    def test_login(self):
        self.client.post(
            "/api/register/", {"username": "user1", "password": "password123"}
        )

        response = self.client.post(
            "/api/login/", {"username": "user1", "password": "password123"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
