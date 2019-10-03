"""Module containing the logic for testing the parent API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Parent

from tag.serializers import ParentSerializer

PARENT_URL = reverse("tags:parent-list")


def sample_parent(user, **params):
    """Create and return a sample recipe.

    :param user: the user to which the parent is associated with
    :param params: additional parameters to pass to the parent object
    :return: new parent object
    """
    defaults = {
        "name": "test_parent",
        "age": 35,
        "address": "123 Fake Street",
        "job": "Test Job"
    }
    defaults.update(params)

    return Parent.objects.create(user=user, **defaults)


class PublicParentApiTest(TestCase):
    """Test unauthenticated recipe API access."""

    def setUp(self):
        """Assign APIClient to class variable

        :return: None
        """
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required.

        :return: None
        :raises AssertionError: fails if no auth is needed to retrieve data
        """
        response = self.client.get(PARENT_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateParentApiTests(TestCase):
    """Test unauthenticated parent API access."""

    def setUp(self):
        """Assign APIClient and a user to class variables.

        :return: None
        """
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes.

        :return: None
        :raises AssertionError: fails when unauthenticated request gets data
        """
        sample_parent(user=self.user)
        sample_parent(user=self.user)

        response = self.client.get(PARENT_URL)

        parents = Parent.objects.all().order_by("-id")
        serializer = ParentSerializer(parents, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_parent_limited_to_user(self):
        """Test retrieving parents for user.

        :return: None
        :raises AssertionError: fails when more than one parents is returned
        """
        user2 = get_user_model().objects.create_user(
            "other@gmail.com",
            "testpass"
        )
        sample_parent(user=user2)
        sample_parent(user=self.user)

        response = self.client.get(PARENT_URL)

        parents = Parent.objects.filter(user=self.user)
        serializer = ParentSerializer(parents, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)
