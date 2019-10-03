"""Module containing the logic for testing the parent API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Parent, Tag, Child

from tag.serializers import ParentSerializer, ParentDetailSerializer

PARENT_URL = reverse("tags:parent-list")


def detail_url(parent_id: int):
    """Return parent detail url.

    :param parent_id: id of the parent object to return details for
    :return: detail parent url
    """
    return reverse("tags:parent-detail", args=[parent_id])


def sample_tag(user, name: str = "test_tag"):
    """Create and return a sample tag.

    :param user: user to associate the tag with
    :param name: name of the tag
    :return: new tag object
    """
    return Tag.objects.create(user=user, name=name)


def sample_child(user, name: str = "test_child"):
    """Create and return a sample child.

    :param user: user to associate the tag with
    :param name: name of the tag
    :return: new child object
    """
    return Child.objects.create(user=user, name=name)


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

    def test_view_parent_detail(self):
        """Test viewing a parent detail.

        :return: None
        :raises AssertionError:
        """
        parent = sample_parent(user=self.user)
        parent.tags.add(sample_tag(user=self.user))
        parent.children.add(sample_child(user=self.user))

        url = detail_url(parent.id)
        response = self.client.get(url)

        serializer = ParentDetailSerializer(parent)
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_parent(self):
        """Test creating parent.

        :return: None
        :raises AssertionError: fails to create a parent object with right data
        """
        payload = {
            "name": "Ted",
            "age": 35,
            "address": "111 Nothing",
            "job": "Test Job"
        }
        response = self.client.post(PARENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        parent = Parent.objects.get(id=response.data["id"])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(parent, key))

    def test_create_parent_with_tags(self):
        """Test creating a recipe with tags.

        :return: None
        :raises AssertionError: fails if both tags aren't in parent
        """
        tag1 = sample_tag(user=self.user, name="Bill")
        tag2 = sample_tag(user=self.user, name="Bob")
        payload = {
            "name": "Helen",
            "tags": [tag1.id, tag2.id],
            "age": 20,
            "address": "123 Whatever",
            "job": "test job"
        }
        response = self.client.post(PARENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        parent = Parent.objects.get(id=response.data["id"])
        tags = parent.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_parent_with_children(self):
        """Test creating a recipe with children.

        :return: None
        :raises AssertionError: fails if both children aren't in parent
        """
        child1 = sample_child(user=self.user, name="Bill")
        child2 = sample_child(user=self.user, name="Bob")
        payload = {
            "name": "Helen",
            "children": [child1.id, child2.id],
            "age": 20,
            "address": "123 Whatever",
            "job": "test job"
        }
        response = self.client.post(PARENT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        parent = Parent.objects.get(id=response.data["id"])
        children = parent.children.all()
        self.assertEqual(children.count(), 2)
        self.assertIn(child1, children)
        self.assertIn(child2, children)
