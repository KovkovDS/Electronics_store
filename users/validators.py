import phonenumbers as phonenumbers
from phonenumbers import NumberParseException
from rest_framework import serializers


class BaseValidator:
    """Базовый класс для проверок."""
    def __init__(self, *fields):
        """Инициализатор класса."""
        self.fields = fields

    def __call__(self, attrs):
        """Вызывается DRF для проверки."""
        field_values = {field: attrs.get(field) for field in self.fields}
        self.validate(**field_values)

    def validate(self, **kwargs):
        """Реализуется в дочерних классах."""
        raise NotImplementedError('Подклассы должны реализовывать этот метод.')


class PhoneNumberValidator(BaseValidator):
    """Класс для валидатора, проверяющего поле "Номер телефона" на корректность данных."""

    def validate(self, phone_number, **kwargs):
        """Метод для проверки."""
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError(
                    'Некорректный формат поля "Номер телефона".'
                )
        except NumberParseException:
            raise serializers.ValidationError(
                    'Обязательное поле "Номер телефона" не заполнено. Укажите корректную информацию.'
                )


class PhoneNumberUpdateValidator(BaseValidator):
    """Класс для валидатора, проверяющего поле "Номер телефона" на корректность данных."""

    def validate(self, phone_number, **kwargs):
        """Метод для проверки."""
        try:
            if phone_number is None:
                pass
            else:
                parsed_number = phonenumbers.parse(phone_number)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise serializers.ValidationError(
                        'Некорректный формат поля "Номер телефона".'
                    )
        except NumberParseException:
            raise serializers.ValidationError(
                    'Обязательное поле "Номер телефона" не заполнено. Укажите корректную информацию.'
                )
