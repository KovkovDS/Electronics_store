from decimal import Decimal
from rest_framework import serializers


class BaseValidator:
    """Базовый класс для проверок."""
    def __init__(self, *fields):
        """ Инициализатор класса. """
        self.fields = fields

    def __call__(self, attrs):
        """Вызывается DRF для проверки."""
        field_values = {field: attrs.get(field) for field in self.fields}
        self.validate(**field_values)

    def validate(self, **kwargs):
        """Реализуется в дочерних классах."""
        raise NotImplementedError('Подклассы должны реализовывать этот метод.')


class SupplierValidator(BaseValidator):
    """Класс для валидатора, исключающего указание ссылки на объект модели "Поставщик" при указании типа звена сети
     продаж как "Завод"."""
    def validate(self, type_point, supplier, **kwargs):
        """Метод для проверки."""
        if type_point is None:
            type_point = "Завод"
            return type_point
        if supplier is not None and type_point == 'Завод':
            raise serializers.ValidationError(
                'Если указано звено сети "Завод", оно не может иметь поставщика. Проверьте корректность вводимых '
                'данных.'
            )


class ArrearsFactoryValidator(BaseValidator):
    """Класс для валидатора, запрещающего указывать ненулевое значение в поле "Задолженность перед поставщиком" при
    указанном типе звена продаже "Завод"."""
    def validate(self, arrears, type_point, **kwargs):
        """Метод для проверки."""
        if arrears is None:
            arrears = 0
            return arrears
        if Decimal(arrears) > 0 and type_point == 'Завод':
            raise serializers.ValidationError(
                'Если указано звено сети "Завод", оно не может иметь положительное значение в поле '
                '"Задолженность перед поставщиком".'
            )


class ArrearsSupplierValidator(BaseValidator):
    """Класс для валидатора, запрещающего указывать ненулевое значение в поле "Задолженность перед поставщиком" при
    пустом поле "Поставщик"."""
    def validate(self, arrears, supplier, **kwargs):
        """Метод для проверки."""
        if arrears is None:
            arrears = 0
            return arrears
        if Decimal(arrears) > 0 and supplier is None:
            raise serializers.ValidationError(
                'Если не указан никакой элемент в поле "Поставщик", "Задолженность перед поставщиком" не может быть '
                'больше нуля.'
            )


class ArrearsValidator(BaseValidator):
    """Класс для валидатора, запрещающего обновлять поле "Задолженность перед поставщиком"."""
    def validate(self, arrears, **kwargs):
        """Метод для проверки."""
        if arrears:
            raise serializers.ValidationError(
                'У Вас не достаточно прав на изменение поля "Задолженность перед поставщиком".'
            )
