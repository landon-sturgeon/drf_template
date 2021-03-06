"""Module containing the logic for testing the parent API."""

import tempfile
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Parent, Tag, Child

from tag.serializers import ParentSerializer, ParentDetailSerializer

PARENT_URL = reverse("tags:parent-list")


def image_upload_url(parent_id):
    """Return url for parent image upload.

    :param parent_id: id of the parent to associate image with
    :return: url of the associated image
    """
    return reverse("tags:parent-upload-image", args=[parent_id])


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

    def test_partial_update_parent(self):
        """Test updating a parent with PATCH.

        :return: None
        :raise AssertionError:
        """
        parent = sample_parent(user=self.user)
        parent.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="funny")

        payload = {"name": "besty", "tags": [new_tag.id]}
        url = detail_url(parent.id)
        self.client.patch(url, payload)

        parent.refresh_from_db()
        self.assertEqual(parent.name, payload["name"])

        tags = parent.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_parent(self):
        """Test updating a parent with PUT.

        :return: None
        :raises AssertionError:
        """
        parent = sample_parent(user=self.user)
        parent.tags.add(sample_tag(user=self.user))
        payload = {
            "name": "Excellent",
            "age": 200,
            "address": "123 Fake Street",
            "job": "test job"
        }
        url = detail_url(parent.id)
        self.client.put(url, payload)
        parent.refresh_from_db()

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(parent, key))

        # a PUT should clear all fields not assigned
        tags = parent.tags.all()
        self.assertEqual(len(tags), 0)


class ParentImageUploadTest(TestCase):
    """Tests the image upload process and associations."""

    def setUp(self):
        """Assign an APIClient and user to the test class.

        :return: None
        """
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)
        self.parent = sample_parent(user=self.user)

    def tearDown(self) -> None:
        """Remove the test image from the /vol/ directory.

        :return: None
        """
        self.parent.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe.

        :return: None
        :raises AssertionError:
        """
        url = image_upload_url(self.parent.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")

            # needed as saving the file points to the end of the file
            # .seek() puts the file pointer back to the beginning of the file
            ntf.seek(0)
            response = self.client.post(
                url, {"image": ntf},
                format="multipart"
            )
        self.parent.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("image", response.data)
        self.assertTrue(os.path.exists(self.parent.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image.

        :return: None
        :raises AssertionError: fails when invalid image is actually uploaded
        """
        url = image_upload_url(self.parent.id)
        response = self.client.post(
            url, {"image": "notimage"}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipes_by_tags(self):
        """Test returning parents with specific tags.

        :return: None
        :raises AssertionError: wrong parent is returned given a tag
        """
        parent1 = sample_parent(user=self.user, name="Bill")
        parent2 = sample_parent(user=self.user, name="Ted")
        tag1 = sample_tag(user=self.user, name="tag1")
        tag2 = sample_tag(user=self.user, name="tag2")
        parent1.tags.add(tag1)
        parent2.tags.add(tag2)
        parent3 = sample_parent(user=self.user, name="this is a test")

        response = self.client.get(
            PARENT_URL,
            {"tags": "{},{}".format(tag1.id, tag2.id)}
        )

        serializer1 = ParentSerializer(parent1)
        serializer2 = ParentSerializer(parent2)
        serializer3 = ParentSerializer(parent3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_parents_by_children(self):
        """Test returning parents with specific children.

        :return: None
        :raises AssertionError: wrong parent is returned given a child
        """
        parent1 = sample_parent(user=self.user, name="Steve")
        parent2 = sample_parent(user=self.user, name="Charles")
        child1 = sample_child(user=self.user, name="child1")
        child2 = sample_child(user=self.user, name="child2")
        parent1.children.add(child1)
        parent2.children.add(child2)
        parent3 = sample_parent(user=self.user, name="what is this??")

        response = self.client.get(
            PARENT_URL,
            {"children": "{},{}".format(child1.id, child2.id)}
        )

        serializer1 = ParentSerializer(parent1)
        serializer2 = ParentSerializer(parent2)
        serializer3 = ParentSerializer(parent3)
        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)
