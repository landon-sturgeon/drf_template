"""Module containing the API views."""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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

    @staticmethod
    def _params_to_ints(query_string):
        """Convert a string of IDs to a list of integers.

        :param query_string: string of ids to be returned
        :return: list of object ids
        """
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        """Return parents for the the authenticated user.

        :return: all the objects associated with the authenticated user
        """
        tags = self.request.query_params.get("tags")
        children = self.request.query_params.get("children")
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if children:
            children_ids = self._params_to_ints(children)
            queryset = queryset.filter(children__id__in=children_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class.

        :return: serializer class
        """
        if self.action == "retrieve":
            return serializers.ParentDetailSerializer
        elif self.action == "upload_image":
            return serializers.ParentImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new parent object.

        :param serializer: parent serializer used to authenticate the user
        :return: new parent object
        """
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk: int = None):
        """Upload an image to a recipe.

        :param request: information being passed to the endpoint
        :param pk: pk of the parent object
        :return: None
        """
        parent = self.get_object()
        serializer = self.get_serializer(
            parent,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
