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


class ParentDetailSerializer(ParentSerializer):
    """Serialize a parent detail."""

    children = ChildSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class ParentImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to parents."""

    class Meta:
        model = Parent
        fields = ("id", "image")
        read_only_fields = ("id", )
