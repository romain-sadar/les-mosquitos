import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from les_mosquitos.mosquitos.models import Label, Point, Parcours

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    user = User.objects.create_user(username="tester", password="test1234")

    token = Token.objects.create(user=user)

    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    return api_client, user


@pytest.fixture
def label():
    return Label.objects.create(
        name="Eau stagnante", color="#00FF00", is_treatable=True
    )


@pytest.fixture
def non_treatable_label():
    return Label.objects.create(name="Zone sèche", color="#FF0000", is_treatable=False)


@pytest.fixture
def point(label, auth_client):
    client, user = auth_client

    return Point.objects.create(
        name="Point test",
        latitude=48.8566,
        longitude=2.3522,
        label=label,
        created_by=user,
    )


@pytest.fixture
def parcours():
    return Parcours.objects.create(name="Mission test")
