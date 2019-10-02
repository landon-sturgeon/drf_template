from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Child
from . import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manages tags in the database."""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Returns objects for the current authenticated user only.

        :return: Returns only authenticated user information
        """
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new tag.

        :param serializer: validation serializer used to create the tag
        :return: None
        """
        serializer.save(user=self.request.user)


class ChildViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manages children in the database."""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    queryset = Child.objects.all()
    serializer_class = serializers.ChildSerializer

    def get_queryset(self):
        """Returns objects for the current authenticated user only.

        :return: Returns only authenticated children information
        """
        return self.queryset.filter(user=self.request.user).order_by("-name")
