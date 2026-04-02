from rest_framework import serializers
from electronics_store.models import Vendor, Contacts, Product
from electronics_store.validators import SupplierValidator, ArrearsValidator
# from datetime import timedelta


class ContactsSerializer(serializers.ModelSerializer):
    """ Класс сериализатора модели "Контакты". """

    class Meta:
        """ Класс для изменения поведения полей сериализатора модели "Контакты". """
        model = Contacts
        fields = '__all__'
        read_only_fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    """ Класс сериализатора модели "Продукт". """

    class Meta:
        """ Класс для изменения поведения полей сериализатора модели "Продукт". """
        model = Product
        fields = '__all__'
        extra_kwargs = {"release_date": {"format": "%d-%m-%Y"}}


class SupplierPreviewSerializer(serializers.ModelSerializer):
    """ Класс сериализатора с ограниченным доступом к модели "Поставщик" (только для чтения). """
    contacts = ContactsSerializer()
    products = ProductSerializer(many=True, required=False)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all(), required=False, allow_null=True)

    class Meta:
        """ Класс для изменения поведения полей сериализатора модели "Поставщик". """
        model = Vendor
        read_only_fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    """ Класс сериализатора с ограниченным доступом к полям модели "Поставщик". """
    contacts = ContactsSerializer()
    products = ProductSerializer(many=True, required=False)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all(), required=False, allow_null=True)

    class Meta:
        """ Класс для изменения поведения полей сериализатора модели "Поставщик". """
        model = Vendor
        fields = '__all__'

    validators = [
        SupplierValidator('type_point', 'supplier'),
        ArrearsValidator('arrears')
    ]


class SupplierUpdateSerializer(serializers.ModelSerializer):
    """ Класс сериализатора модели "Поставщик". """
    contacts = ContactsSerializer()
    products = ProductSerializer(many=True, required=False)
    supplier = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all(), required=False, allow_null=True)

    class Meta:
        """ Класс для изменения поведения полей сериализатора модели "Поставщик". """
        model = Vendor
        fields = '__all__'

    validators = [
        SupplierValidator('type_point', 'supplier'),
    ]
