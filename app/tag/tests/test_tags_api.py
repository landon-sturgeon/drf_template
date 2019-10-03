"""Module containing the test logic for the tags model."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Parent

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

    def test_create_tag_successful(self):
        """Tests creating a new tag.

        :return: None
        :raises AssertionError: fails if the tag isn't created
        """
        payload = {"name": "Test tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with an invalid payload.

        :return: None
        :raises AssertionError: fails when an invalid payload creates a tag
        """
        payload = {"name": ""}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_parents(self):
        """Test filtering tags by those assigned to parents.

        :return: None
        :raises AssertionError: fails when recipes without the tag are returned
        """
        tag1 = Tag.objects.create(user=self.user, name="tag1")
        tag2 = Tag.objects.create(user=self.user, name="tag2")
        parent = Parent.objects.create(
            name="parent",
            age=1,
            address="address 1",
            job="job 1",
            user=self.user
        )
        parent.tags.add(tag1)
        response = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2, response.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items.

        :return: None
        :raises AssertionError: fails when both tags are returned
        """
        tag1 = Tag.objects.create(user=self.user, name="tag1")
        Tag.objects.create(user=self.user, name="tag2")
        parent1 = Parent.objects.create(
            name="parent1",
            age=1,
            address="address 1",
            job="job 1",
            user=self.user
        )
        parent1.tags.add(tag1)
        parent2 = Parent.objects.create(
            name="parent2",
            age=2,
            address="address 2",
            job="job 2",
            user=self.user
        )
        parent2.tags.add(tag1)

        response = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)
