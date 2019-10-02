"""Package containing the code for the user API views."""
from rest_framework import generics

from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    serializer_class = UserSerializer
