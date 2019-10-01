from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    """Custom user manager overriding the base user manager functions."""

    def create_user(self, email: str, password: str = None, **extra_fields):
        """Create and saves a new user with an email and a password if it exists.

        Also accepts additional fields, parsed as *args.

        :param email: Email address of the user
        :param password: Password the user applies to their account
        :param extra_fields: any additional data about the user
        :return: user created and saved
        """
        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None):
        """Create and saves a new superuser with an email and a password.

        :param email: email of the superuser (will be used as username)
        :param password: password of the superuser
        :return: superuser created and saved
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"
