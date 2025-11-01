from django.db import models
from mptt.models import MPTTModel


class VendorType(models.Choices):
    FACTORY = 'Завод'
    IE = 'ИП'
    RN = 'Розничная сеть'


class Vendor(models.Model):
    """
    Модель поставщика
    """
    name = models.CharField(unique=True, max_length=200, verbose_name="Наименование", db_index=True)
    type = models.CharField(choices=VendorType.choices, default=VendorType.FACTORY, verbose_name='Тип')
    contacts = models.ForeignKey('Contacts', on_delete=models.CASCADE, verbose_name='Контакты')
    email = models.EmailField(blank=True, verbose_name="E-mail")
    products = models.ManyToManyField('Product', verbose_name='Товар', db_index=True)
    arrears = models.FloatField(null=True, blank=True, verbose_name="Задолженность перед поставщиком")
    release_date = models.DateTimeField(auto_now_add=True, verbose_name="Время создания", db_index=True)
    parent = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                               db_index=True, verbose_name='Поставщик')
    supplier_level = models.IntegerField(blank=True, verbose_name="Уровень")

    def __str__(self):
        return f'{self.type} {self.name} {self.email}'

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ["parent", "name", "type", "email"]


class Contacts(models.Model):
    country = models.CharField(max_length=200, verbose_name="Страна")
    city = models.CharField(max_length=200, verbose_name="Город")
    street = models.CharField(max_length=200, verbose_name="Улица")
    house = models.CharField(max_length=200, verbose_name="Дом")

    def __str__(self):
        return f"{self.country}, {self.city}, {self.street}. {self.house}"

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'
        ordering = ["country", "city", "street", "house"]


class Product(models.Model):
    name = models.CharField(unique=True, max_length=200, verbose_name="Наименование", db_index=True)
    model = models.CharField(unique=True, max_length=200, verbose_name="Модель", db_index=True)
    release_date = models.DateField(auto_now_add=True, verbose_name="Дата выхода продукта", db_index=True)

    def __str__(self):
        return f"{self.name} {self.model}"

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ["model", "name"]
