"""Package containing the tests for the user api."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    """Creates a new user.

    :param params: additional parameters to pass to the user created
    :return: new user object
    """
    return get_user_model().objects.create_user(**params)


class PublicUsersAPITests(TestCase):
    """Class dedicated to testing the users api available to the public."""

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

    def test_create_token_for_user(self):
        """Test that a token is created for the user.

        :return: None
        :raises AssertionError: token doesn't exists in response
        """
        payload = {
            "email": "test@gmail.com",
            "password": "testpass"
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given.

        :return: None
        :raises AssertionError: token given with invalid credentials
        """
        create_user(
            email="test@gmail.com",
            password="testpass"
        )
        payload = {
            "email": "test@gmail.com",
            "password": "wrong"
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist.

        :return: None
        :raises AssertionError: user exists when not created in the first place
        """
        payload = {
            "email": "test@gmail.com",
            "password": "testpass"
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required.

        :return: None
        :raises AssertionError: user created without a password
        """
        response = self.client.post(
            TOKEN_URL,
            {"email": "one", "password": ""}
        )
        self.assertNotIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users.

        :return: None
        :raises AssertionError: when retreiving user info is allowed
        """
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        """Assign the class' user to a known users.

        :return: None
        """
        self.user = create_user(
            email="test@gmail.com",
            password="testpass",
            name="fname"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in used.

        :return: None
        :raises AssertionError: fails to retrieve the proper user
        """
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "name": self.user.name,
            "email": self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url.

        :return: None
        :raise AssertionError: fails to prevent a post to the user profile
        """
        response = self.client.post(ME_URL, {})

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user.

        :return: None
        :raises AssertionError:
        """
        payload = {'name': 'new name', 'password': 'newpassword123'}

        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
