from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Child, Parent
from . import serializers


class BaseApiAttrViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin):
    """Base view set for user owned API endpoints."""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Return objects for the current authenticated user only.

        :return: all the objects associated with the authenticated user
        """
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new object

        :param serializer: validation serializer used to create the object
        :return: None
        """
        serializer.save(user=self.request.user)


class TagViewSet(BaseApiAttrViewSet):
    """Manages tags in the database."""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class ChildViewSet(BaseApiAttrViewSet):
    """Manages children in the database."""

    queryset = Child.objects.all()
    serializer_class = serializers.ChildSerializer


class ParentViewSet(viewsets.ModelViewSet):
    """Manages parents in the database"""

    serializer_class = serializers.ParentSerializer
    queryset = Parent.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """Return parents for the the authenticated user.

        :return: all the objects associated with the authenticated user
        """
        return self.queryset.filter(user=self.request.user)
