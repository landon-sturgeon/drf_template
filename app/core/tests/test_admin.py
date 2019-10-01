"""Package testing our admin functions."""

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Custom test class, testing our admin page and functionality."""

    def setUp(self):
        """Creates a test client, superuser that's logged in, and a user.

        :return: sets class' self.client variable to new user
        """
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            password="password123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="password123",
            name="test user Full Name"
        )

    def test_users_listed(self):
        """Test that users are listed on user page.

        :return: None
        :raises AssertionError: user doesn't have a name or email
        """
        url = reverse("admin:core_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works.

        :return: None
        :raises AssertionError: user change page returns 200 for user
        """
        url = reverse("admin:core_user_change", args=[self.user.id])
        # /admin/core/user/`n`/

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works.

        :return: None
        :raises AssertionError: add user page returns 200 when adding user
        """
        url = reverse("admin:core_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
