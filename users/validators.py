import phonenumbers as phonenumbers
from rest_framework import serializers


class BaseValidator:
    """ Базовый класс для проверок. """
    def __init__(self, *fields):
        """ Инициализатор класса. """
        self.fields = fields

    def __call__(self, attrs):
        """ Вызывается DRF для проверки. """
        field_values = {field: attrs.get(field) for field in self.fields}
        self.validate(**field_values)

    def validate(self, **kwargs):
        """ Реализуется в дочерних классах. """
        raise NotImplementedError('Подклассы должны реализовывать этот метод.')


class PhoneNumberValidator(BaseValidator):
    """ Проверяет поле "Номер телефона" на корректность данных. """

    def validate(self, phone_number, **kwargs):
        """Метод для проверки."""
        parsed_number = phonenumbers.parse(phone_number)
        if not phonenumbers.is_valid_number(parsed_number):
            raise serializers.ValidationError(
                'Некорректный формат поля "Номер телефона".'
            )
