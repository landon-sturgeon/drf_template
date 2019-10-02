"""Module containing the logic for the tag serializers."""

from rest_framework import serializers

from core.models import Tag, Child


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects."""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id", )


class ChildSerializer(serializers.ModelSerializer):
    """Serializer for child objects."""

    class Meta:
        model = Child
        fields = ("id", "name")
        read_only_fields = ("id", )
