from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Generic TestCase class for testing our models."""

    def test_create_user_with_email_successful(self):
        """Test creating a new user when an email is successful.

        :return: None
        :raises AssertionError: is the user was created with an invalid email
        """
        email = "test@gmail.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
