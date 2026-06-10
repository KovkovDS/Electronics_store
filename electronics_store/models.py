from django.db import models
from mptt.models import MPTTModel


class Product(models.Model):
    """Класс модели "Продукт"."""
    name = models.CharField(max_length=200, verbose_name='Наименование', db_index=True)
    model = models.CharField(max_length=200, verbose_name='Модель', db_index=True)
    release_date = models.DateField(auto_now_add=True, verbose_name='Дата выхода продукта', db_index=True)

    def __str__(self):
        """Метод для описания человеко читаемого вида модели "Продукт"."""
        return f'{self.name} {self.model}'

    class Meta:
        """Класс для изменения поведения полей модели "Продукт"."""
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['model', 'name', 'release_date']


class Contacts(models.Model):
    """Класс модели "Контакты"."""
    email = models.EmailField(verbose_name='Почта')
    country = models.CharField(max_length=200, verbose_name='Страна')
    city = models.CharField(max_length=200, verbose_name='Город')
    street = models.CharField(max_length=200, verbose_name='Улица')
    house = models.CharField(max_length=200, verbose_name='Дом')

    def __str__(self):
        """Метод для описания человеко читаемого вида модели "Контакты"."""
        return f'{self.email}, {self.country}, {self.city}, {self.street}. {self.house}'

    class Meta:
        """Класс для изменения поведения полей модели "Контакты"."""
        verbose_name = 'Контакты'
        verbose_name_plural = 'Контакты'
        ordering = ['email', 'country', 'city', 'street', 'house']


class VendorType(models.TextChoices):
    """Модель "Тип звена сети продаж"."""
    FACTORY = 'Завод'
    IE = 'Индивидуальный предприниматель'
    RN = 'Розничная сеть'


class Vendor(models.Model):
    """Класс модели "Поставщика"."""
    name = models.CharField(unique=True, max_length=200, verbose_name='Наименование', db_index=True)
    type_point = models.CharField(choices=VendorType.choices, default=VendorType.FACTORY,
                                  verbose_name='Тип звена сети продаж')
    contacts = models.ForeignKey('Contacts', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Контакты',
                                 related_name='ul')
    products = models.ManyToManyField('Product', verbose_name='Товар', blank=True, related_name='vendors',
                                      db_index=True)
    arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Задолженность перед '
                                                                                           'поставщиком')
    release_date = models.DateTimeField(auto_now_add=True, verbose_name='Время создания', db_index=True)
    supplier = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='distributor',
                                 db_index=True, verbose_name='Поставщик')

    def __str__(self):
        """Метод для описания человеко читаемого вида модели "Поставщик"."""
        return f'{self.type_point} {self.name} {self.contacts.email}'

    class Meta:
        """Класс для изменения поведения полей модели "Поставщик"."""
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name', 'type_point', 'contacts__city', 'arrears']
