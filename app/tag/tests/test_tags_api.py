"""Module containing the test logic for the tags model."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from ..serializers import TagSerializer


TAGS_URL = reverse("tags:tag-list")


class PublicTagsApiTests(TestCase):
    """Tests the publicly available tags API."""

    def setUp(self):
        """Adds an APIClient to the class.

        :return: None
        """
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags.

        :return: None
        :raises AssertionError: fails with no auth needed to get tags
        """
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API."""

    def setUp(self):
        """Adds a user to the class.

        :return: None
        """
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "password"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags.

        :return: None
        :raises AssertionError: fails when not all tags are retrieved
        """
        Tag.objects.create(user=self.user, name="test1")
        Tag.objects.create(user=self.user, name="test2")

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        # many flag true to serialize all objects
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user.

        :return: None
        :raises AssertionError: fails when incorrect tags for user returned
        """
        user2 = get_user_model().objects.create_user(
            "other@gmail.com",
            "testpass"
        )
        Tag.objects.create(user=user2, name="user2")
        tag = Tag.objects.create(user=self.user, name="test tag")

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # make sure it returns only one tag
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], tag.name)
