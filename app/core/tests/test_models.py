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

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized.

        :return: None
        :raises AssertionError: exception if the user email is not normalized
        """
        email = "test@GMAIL.com"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email, raising error.

        :return: None
        :raises AssertionError: user with no email doesn't respond
                                with ValueError
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """Test creating a new superuser.

        :return: None
        :raises AssertionError:
        """
        user = get_user_model().objects.create_superuser(
            "test@gmail.com",
            "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
