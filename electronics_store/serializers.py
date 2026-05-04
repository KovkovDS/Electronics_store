from rest_framework import serializers
from electronics_store.models import Vendor, Contacts, Product
from electronics_store.validators import SupplierValidator, ArrearsValidator


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


class SupplierSerializer(serializers.ModelSerializer):
    """ Класс сериализатора с ограниченным доступом к полям модели "Поставщик". """
    contacts = ContactsSerializer(required=False)
    products = ProductSerializer(many=True, required=False)
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        """ Класс для изменения поведения полей сериализатора модели "Поставщик". """
        model = Vendor
        fields = '__all__'
        read_only_fields = ['id']

        validators = [
            SupplierValidator('type_point', 'supplier'),
            ArrearsValidator('arrears')
        ]

    def create(self, validated_data):
        """ Метод передачи данных в сериализатор при сохранении данных. """

        contacts_data = validated_data.pop("contacts")
        products_data = validated_data.pop("products", [])

        contacts = Contacts.objects.create(**contacts_data)
        supplier = Vendor.objects.create(contacts=contacts, **validated_data)

        for product_data in products_data:
            product, _ = Product.objects.get_or_create(**product_data)
            supplier.products.add(product)

        return supplier

    def update(self, instance, validated_data):
        """ Метод передачи данных в сериализатор при сохранении данных. """

        instance.title = validated_data.get("name", instance.name)
        instance.type_point = validated_data.get("type_point", instance.type_point)
        instance.arrears = validated_data.get("arrears", instance.arrears)
        instance.supplier = validated_data.get("supplier", instance.supplier)

        if instance.type_point == "Завод" and instance.supplier is not None:
            raise serializers.ValidationError(
                'Если указано звено сети "Завод", оно не может иметь поставщика. Проверьте корректность вводимых '
                'данных'
            )

        contacts_data = validated_data.get("contacts", {})
        contacts_serializer = ContactsSerializer(instance.contacts, data=contacts_data, partial=True)
        if contacts_serializer.is_valid():
            contacts_serializer.save()

        if "products" in validated_data:
            instance.products.clear()
            for product_data in validated_data["products"]:
                product, _ = Product.objects.get_or_create(**product_data)
                instance.products.add(product)

        instance.save()
        return instance


class SupplierAdminRootSerializer(serializers.ModelSerializer):
    """ Класс сериализатора модели "Поставщик". """
    contacts = ContactsSerializer(required=False)
    products = ProductSerializer(many=True, required=False)
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        """ Класс для изменения поведения полей сериализатора модели "Поставщик". """
        model = Vendor
        fields = '__all__'
        validators = [
            SupplierValidator('type_point', 'supplier')
        ]

    def create(self, validated_data):
        """ Метод передачи данных в сериализатор при сохранении данных. """

        contacts_data = validated_data.pop("contacts")
        products_data = validated_data.pop("products", [])

        contacts = Contacts.objects.create(**contacts_data)
        supplier = Vendor.objects.create(contacts=contacts, **validated_data)

        for product_data in products_data:
            product, _ = Product.objects.get_or_create(**product_data)
            supplier.products.add(product)

        return supplier

    def update(self, instance, validated_data):
        """ Метод передачи данных в сериализатор при обновлении данных. """

        instance.title = validated_data.get("name", instance.name)
        instance.type_point = validated_data.get("type_point", instance.type_point)
        instance.arrears = validated_data.get("arrears", instance.arrears)
        instance.supplier = validated_data.get("supplier", instance.supplier)

        if instance.type_point == "Завод" and instance.supplier is not None:
            raise serializers.ValidationError(
                'Если указано звено сети "Завод", оно не может иметь поставщика. Проверьте корректность вводимых '
                'данных'
            )

        contacts_data = validated_data.get("contacts", {})
        contacts_serializer = ContactsSerializer(instance.contacts, data=contacts_data, partial=True)
        if contacts_serializer.is_valid():
            contacts_serializer.save()

        if "products" in validated_data:
            instance.products.clear()
            for product_data in validated_data["products"]:
                product, _ = Product.objects.get_or_create(**product_data)
                instance.products.add(product)

        instance.save()
        return instance
