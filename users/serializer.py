from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import User
from users.validators import PhoneNumberValidator


class ProfileUserSerializer(serializers.ModelSerializer):
    """Класс сериализатора пользователя."""

    @staticmethod
    def validate_password(value: str) -> str:
        """
        Hash value passed by user.

        :param value: пароль пользователя
        :return: возвращает пароль в хэшированном виде
        """
        return make_password(value)

    class Meta:
        """Класс для изменения поведения полей сериализатора модели "Пользователь"."""

        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'city', 'password']
        validators = [
            PhoneNumberValidator('phone_number')
        ]


class ProfileSerializer(serializers.ModelSerializer):
    """Класс сериализатора пользователя."""

    @staticmethod
    def validate_password(value: str) -> str:
        """
        Hash value passed by user.

        :param value: пароль пользователя
        :return: возвращает пароль в хэшированном виде
        """
        return make_password(value)

    class Meta:
        """Класс для изменения поведения полей сериализатора модели "Пользователь"."""

        model = User
        fields = '__all__'
        validators = [
            PhoneNumberValidator('phone_number')
        ]


class ProfilePreviewSerializer(serializers.ModelSerializer):
    """Класс сериализатора с ограниченным доступом к модели пользователя."""

    class Meta:
        """Класс для изменения поведения полей сериализатора модели "Пользователь"."""

        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'city', 'is_active']
        read_only_fields = ['email', 'first_name', 'last_name', 'phone_number', 'city', 'is_active']
        validators = [
            PhoneNumberValidator('phone_number')
        ]


class CreateProfileSerializer(serializers.ModelSerializer):
    """Класс сериализатора для создания пользователя с базовым доступом."""
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        """Класс для изменения поведения полей сериализатора модели "Пользователь"."""

        model = User
        fields = '__all__'
        validators = [
            PhoneNumberValidator('phone_number')
        ]
