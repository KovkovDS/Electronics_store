from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import User
from users.validators import PhoneNumberValidator, PhoneNumberUpdateValidator


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
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'city', 'is_active', 'is_staff', 'is_superuser',
                  'password']
        validators = [
            PhoneNumberValidator('phone_number')
        ]


class ProfileUpdateUserSerializer(serializers.ModelSerializer):
    """Класс сериализатора пользователя."""
    phone_number = serializers.CharField(allow_null=True, required=False)

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
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'city', 'is_active', 'is_staff', 'is_superuser',
                  'password']
        validators = [
            PhoneNumberUpdateValidator('phone_number')
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
        extra_kwargs = {"create_at": {"format": "%d-%m-%Y"}, "updated_at": {"format": "%d-%m-%Y"}}


class ProfileViewingSerializer(serializers.ModelSerializer):
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
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'city', 'is_staff', 'is_superuser', 'password']
        validators = [
            PhoneNumberValidator('phone_number')
        ]
