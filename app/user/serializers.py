"""Package containing the serializer used by the user model."""

from django.contrib.auth import get_user_model, authenticate
from django.utils. translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object."""

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5
            }
        }

    def create(self, validated_data):
        """Create a new user with encrypted password and return it.

        :param validated_data: data needed to create a new user
        :return: new user object
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Updates a user, setting and password correctly and returns it.

        :param instance: user model
        :param validated_data: fields that are going through the update
        :return: updated user object
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object."""

    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user.

        :param attrs: attributes that need to be validated
        :return: attrs with authenticated and validated user field
        """
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password
        )

        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
