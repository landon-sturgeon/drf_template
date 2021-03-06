import uuid
import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings


def parent_image_file_path(instance, filename):
    """Generate file path for the new parent image.

    :param instance: instance of parent object that's creating the path
    :param filename: original filename of the image file
    :return: filepath of the new image
    """
    extension = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"

    return os.path.join("uploads/parent/", filename)


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


class Tag(models.Model):
    """Tag to be used for an object."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """Return the name of the tag.

        :return: String of the tag's name
        """
        return self.name


# This serves just as an example of how to create new generic objects into db
class Child(models.Model):
    """Generic Object to be used later."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Return the name of the child object.

        :return: string of name of the child object
        """
        return self.name


class Parent(models.Model):
    """Generic parent object to be used later."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    age = models.IntegerField()
    job = models.CharField(max_length=255)

    # many-to-many fields
    children = models.ManyToManyField("Child")
    tags = models.ManyToManyField("Tag")

    # image field
    image = models.ImageField(null=True, upload_to=parent_image_file_path)

    def __str__(self):
        """Return the name of the parent object.

        :return: string of the name of the parent object
        """
        return self.name
