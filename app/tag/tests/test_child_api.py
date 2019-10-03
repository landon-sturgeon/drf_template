"""Module containing the tests for the child object."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Child, Parent

from tag.serializers import ChildSerializer


CHILD_URL = reverse("tags:child-list")


class PublicChildApiTests(TestCase):
    """Test the publicly available child API."""

    def setUp(self):
        """Assign an APIClient() to the class' client variable.

        :return: None
        """
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint.

        :return: None
        :raise AssertionError: fails if status ok without login
        """
        response = self.client.get(CHILD_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private child can be retrieved by authorized user."""

    def setUp(self):
        """Assign an APIClient() and user to the class' variables.

        :return: None
        """
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "password"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_child_list(self):
        """Test retrieving a list of children.

        :return: None
        :raises AssertionError: fails if a list of child objects isn't returned
        """
        Child.objects.create(user=self.user, name="test1")
        Child.objects.create(user=self.user, name="test2")

        response = self.client.get(CHILD_URL)

        children = Child.objects.all().order_by("-name")
        serializer = ChildSerializer(children, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_children_limited_to_user(self):
        """Test that children for the authenticated user are returned.

        :return: None
        :raises AssertionError: fails if non-authenticated children returned
        """
        user2 = get_user_model().objects.create_user(
            "other@gmail.com",
            "testpass"
        )
        Child.objects.create(user=user2, name="test_name")
        child = Child.objects.create(user=self.user, name="test_name2")

        response = self.client.get(CHILD_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], child.name)

    def test_create_child_successful(self):
        """Test creating a new child.

        :return: None
        :raises AssertException: fails creating a new child object
        """
        payload = {"name": "testname"}
        self.client.post(CHILD_URL, payload)

        exists = Child.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails.

        :return: None
        :raises AssertException: creates a child object with invalid payload
        """
        payload = {"name": ""}
        response = self.client.post(CHILD_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_children_assigned_to_parents(self):
        """Test filtering children by those assigned to parents.

        :return: None
        :raises AssertionError: fails when parents without the tag are returned
        """
        child1 = Child.objects.create(user=self.user, name="child1")
        child2 = Child.objects.create(user=self.user, name="child2")
        parent = Parent.objects.create(
            name="parent",
            age=1,
            address="address 1",
            job="job 1",
            user=self.user
        )
        parent.children.add(child1)
        response = self.client.get(CHILD_URL, {"assigned_only": 1})

        serializer1 = ChildSerializer(child1)
        serializer2 = ChildSerializer(child2)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2, response.data)

    def test_retrieve_children_assigned_unique(self):
        """Test filtering children by assigned returns unique items.

        :return: None
        :raises AssertionError: fails when both children are returned
        """
        child1 = Child.objects.create(user=self.user, name="child1")
        Child.objects.create(user=self.user, name="child2")
        parent1 = Parent.objects.create(
            name="parent1",
            age=1,
            address="address 1",
            job="job 1",
            user=self.user
        )
        parent1.children.add(child1)
        parent2 = Parent.objects.create(
            name="parent2",
            age=2,
            address="address 2",
            job="job 2",
            user=self.user
        )
        parent2.children.add(child1)

        response = self.client.get(CHILD_URL, {"assigned_only": 1})

        self.assertEqual(len(response.data), 1)
