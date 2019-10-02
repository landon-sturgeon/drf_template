"""Package containing the tests for the user api."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")


def create_user(**params):
    """Creates a new user.

    :param params: additional parameters to pass to the user created
    :return: new user object
    """
    return get_user_model().objects.create_user(**params)


class PublicUsersAPITests(TestCase):
    """Test class dedicated to testing the users api available to the public."""

    def setUp(self):
        """Assigns the self.client of the class to an instance of APIClient.

        :return: None
        """
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful.

        :return: None
        :raises AssertionException: user isn't created with a proper payload
        """
        payload = {
            "email": "test@gmail.com",
            "password": "testpass",
            "name": "test Name"
        }
        response = self.client.post(CREATE_USER_URL, payload)

        # check to make sure we get 201 response (successful creation)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload["password"]))

        # check to make sure that the password isn't sent with the payload
        self.assertNotIn("password", response.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails.

        :return: None
        :raises AssertionError: creates a user when one already exists
        """
        payload = {
            "email": "test@gmail.com",
            "password": "testpass",
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        # make sure it's a bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters.

        :return: None
        :raises AssertionError: user created with a password that is too short
        """
        payload = {
            "email": "test@gmail.com",
            "password": "pw"
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)
