"""Module containing the logic for the tag serializers."""

from rest_framework import serializers

from core.models import Tag, Child, Parent


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


class ParentSerializer(serializers.ModelSerializer):
    """Serializer for parent objects."""
    children = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Child.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Parent
        fields = ("id", "name", "age", "address", "job", "children", "tags")
        read_only_fields = ("id", )
