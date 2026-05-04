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


class SupplierValidator(BaseValidator):
    """ Исключает указание ссылки на объект модели "Поставщик" при указании типа звена сети продаж как "Завод". """
    def validate(self, type_point, supplier, **kwargs):
        if type_point == "Завод" and supplier is not None:
            raise serializers.ValidationError(
                'Если указано звено сети "Завод", оно не может иметь поставщика. Проверьте корректность вводимых '
                'данных'
            )


class ArrearsValidator(BaseValidator):
    """ Запрещает обновлять поле "Задолженность перед поставщиком". """
    def validate(self, arrears, **kwargs):
        """Метод для проверки."""
        if arrears:
            raise serializers.ValidationError(
                'У Вас не достаточно прав на изменение поля "Задолженность перед поставщиком".'
            )
