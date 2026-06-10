from random import randint
import pytest
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from factories import UserFactory, UserAdminFactory, ContactsFactory, ProductFactory, VendorFactory
from electronics_store.models import VendorType, Vendor, Contacts, Product
from electronics_store.serializers import SupplierAdminRootSerializer, SupplierSerializer, ContactsSerializer, \
    ProductSerializer
from electronics_store.validators import SupplierValidator, ArrearsFactoryValidator, ArrearsSupplierValidator, \
    ArrearsValidator
from users.models import User


class TestBaseData(APITestCase):
    """Класс с первичными данными для тестов эндпоинтов для модели "Поставщик"."""

    def setUp(self):
        """ Метод класса с начальными данными для тестов."""
        self.admin = UserAdminFactory.create(is_active=True)
        self.user = UserFactory.create(is_active=True)
        self.contacts1 = ContactsFactory.create()
        self.contacts1.save()
        self.product1 = ProductFactory.create()
        self.product1.save()
        self.product2 = ProductFactory.create()
        self.product2.save()
        self.product3 = ProductFactory.create()
        self.product3.save()
        self.vendor1 = VendorFactory.create(contacts=self.contacts1, type_point=VendorType.FACTORY, arrears='0.00')
        self.vendor1.save()
        self.vendor1.products.set([self.product1, self.product2, self.product3])
        self.vendor2 = VendorFactory.create(contacts=self.contacts1, type_point=VendorType.FACTORY, arrears='0.00')
        self.vendor2.save()
        self.vendor2.products.set([self.product1])
        self.url = reverse('electronics_store:adding_supplier')


class SupplierCreateTest(TestBaseData):
    """Класс тестов для эндпоинта создания звена сети продаж электроники."""

    @pytest.mark.django_db
    def test_supplier_create_admin_root_successful(self):
        """Тест создания звена сети продажи электроники с отсутствием ошибок."""

        self.assertEqual(Vendor.objects.count(), 2)
        self.assertEqual(Contacts.objects.count(), 1)
        self.assertEqual(Product.objects.count(), 3)
        self.contacts2 = ContactsFactory.create()
        self.contacts2.save()
        self.vendor3 = VendorFactory.create(contacts=self.contacts2, type_point=VendorType.FACTORY, arrears='0.00')
        self.vendor3.save()
        self.vendor3.products.set([self.product2, self.product3])
        self.url = reverse('electronics_store:adding_supplier')
        self.client.force_authenticate(user=self.admin)
        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor3, many=False)
        form_data = self.serializer_vendor.data
        self.vendor3.delete()
        self.contacts2.delete()
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vendor.objects.count(), 3)
        self.assertEqual(Contacts.objects.count(), 2)
        self.assertEqual(Product.objects.count(), 3)
        supplier = Vendor.objects.filter(name=response.data['name']).first()
        self.serializer_vendor_new = SupplierAdminRootSerializer(supplier, many=False)
        self.assertEqual(self.serializer_vendor_new.data, response.data)

    @pytest.mark.django_db
    def test_supplier_create_invalid_url(self):
        """Тест создания звена сети продажи электроники с некорректным запросом."""

        self.contacts2 = ContactsFactory.create()
        self.contacts2.save()
        self.vendor3 = VendorFactory.create(contacts=self.contacts2, type_point=VendorType.FACTORY, arrears='0.00')
        self.vendor3.save()
        self.vendor3.products.set([self.product2, self.product3])
        self.url = reverse('electronics_store:adding_supplier')
        self.client.force_authenticate(user=self.admin)
        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor3, many=False)
        form_data = self.serializer_vendor.data
        response = self.client.post('/suplier/new/', data=form_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_supplier_create_admin_root_user_no_active(self):
        """Тест создания звена сети продажи электроники с проверкой на получение ошибки не активности
        пользователя."""

        self.url = reverse('electronics_store:adding_supplier')
        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor2, many=False)
        form_data = self.serializer_vendor.data
        self.vendor2.delete()
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_supplier_create_admin_root_error_supplier(self):
        """Тест создания звена сети продажи электроники с проверкой на получение ошибки валидации по полю
        "Поставщик"."""

        self.url = reverse('electronics_store:adding_supplier')
        self.vendor2.supplier = self.vendor1
        self.client.force_authenticate(user=self.admin)
        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor2, many=False)
        form_data = self.serializer_vendor.data
        self.vendor2.delete()
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = SupplierValidator('type_point', 'supplier')
            validator(form_data)
        self.assertEqual(response.json().get('error', 'Если указано звено сети "Завод", оно не может иметь поставщика. '
                                                      'Проверьте корректность вводимых данных.'),
                         'Если указано звено сети "Завод", оно не может иметь поставщика. '
                         'Проверьте корректность вводимых данных.')

    @pytest.mark.django_db
    def test_supplier_create_admin_root_error_arrears_because_type_point(self):
        """Тест создания звена сети продажи электроники с проверкой на получение ошибки валидации по полю
        "Задолженность перед поставщиком" из-за некорректности данных для поля "Тип звена сети продаж"."""

        self.url = reverse('electronics_store:adding_supplier')
        self.vendor2.arrears = 10000
        self.client.force_authenticate(user=self.admin)
        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor2, many=False)
        form_data = self.serializer_vendor.data
        self.vendor2.delete()
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = ArrearsFactoryValidator('type_point', 'arrears')
            validator(form_data)
        self.assertEqual(response.json().get('error', 'Если указано звено сети "Завод", оно не может иметь '
                                                      'положительное значение в поле '
                                                      '"Задолженность перед поставщиком".'),
                         'Если указано звено сети "Завод", оно не может иметь положительное значение в поле '
                         '"Задолженность перед поставщиком".')

    @pytest.mark.django_db
    def test_supplier_create_admin_root_error_arrears_because_supplier(self):
        """Тест создания звена сети продажи электроники с проверкой на получение ошибки валидации по полю
        "Задолженность перед поставщиком" из-за некорректности данных для поля "Поставщик"."""

        self.url = reverse('electronics_store:adding_supplier')
        self.vendor1.type_point = VendorType.IE
        self.vendor1.arrears = 10000
        self.client.force_authenticate(user=self.admin)
        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor1, many=False)
        form_data = self.serializer_vendor.data
        self.vendor1.delete()
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = ArrearsSupplierValidator('arrears', 'supplier')
            validator(form_data)
        self.assertEqual(response.json().get('error', 'Если не указан никакой элемент в поле "Поставщик", '
                                                      '"Задолженность перед поставщиком" не может быть больше нуля.'),
                         'Если не указан никакой элемент в поле "Поставщик", "Задолженность перед поставщиком" не '
                         'может быть больше нуля.')

    @pytest.mark.django_db
    def test_supplier_create_successful(self):
        """Тест создания звена сети продажи электроники с успешным запросом."""

        self.assertEqual(Vendor.objects.count(), 2)
        self.assertEqual(Contacts.objects.count(), 1)
        self.assertEqual(Product.objects.count(), 3)
        self.contacts2 = ContactsFactory.create()
        self.contacts2.save()
        self.vendor3 = VendorFactory.create(contacts=self.contacts2, type_point=VendorType.IE, arrears='0.00',
                                            supplier=self.vendor2)
        self.vendor3.save()
        self.vendor3.products.set([self.product2, self.product3])
        self.url = reverse('electronics_store:adding_supplier')
        self.client.force_authenticate(user=self.user)
        self.serializer_vendor = SupplierSerializer(self.vendor3, many=False)
        form_data = self.serializer_vendor.data
        self.vendor3.delete()
        self.contacts2.delete()
        response = self.client.post(self.url, data=form_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Vendor.objects.count(), 3)
        self.assertEqual(Contacts.objects.count(), 2)
        self.assertEqual(Product.objects.count(), 3)
        distributor = Vendor.objects.filter(name=response.data['name']).first()
        self.serializer_vendor_new = SupplierAdminRootSerializer(distributor, many=False)
        self.assertEqual(self.serializer_vendor_new.data, response.data)

    @pytest.mark.django_db
    def test_supplier_create_error_because_no_authorization_required(self):
        """Тест создания звена сети продажи электроники с проверкой на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor2, many=False)
        self.url = reverse('electronics_store:adding_supplier')
        form_data = self.serializer_vendor.data
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class SuppliersViewingTest(TestBaseData):
    """Класс тестов для эндпоинта просмотра информации о звене сети продаж электроники."""

    @pytest.mark.django_db
    def test_supplier_viewing_successful(self):
        """Тест на получение информации о звене сети продажи электроники с успешным запросом."""

        self.url = reverse('electronics_store:supplier', kwargs={'pk': self.vendor2.pk})
        self.vendor2.type_point = VendorType.IE
        self.vendor2.supplier = self.vendor1
        self.vendor2.save()
        self.serializer_vendor = SupplierSerializer(self.vendor2, many=False)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.serializer_vendor.data)

    @pytest.mark.django_db
    def test_supplier_viewing_admin_root_successful(self):
        """Тест на получение информации о звене сети продажи электроники с успешным запросом от администратора."""

        self.serializer_vendor = SupplierAdminRootSerializer(self.vendor2, many=False)
        self.url = reverse('electronics_store:supplier', kwargs={'pk': self.vendor2.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.serializer_vendor.data)

    @pytest.mark.django_db
    def test_supplier_viewing_invalid_pk(self):
        """Тест на получение информации о звене сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:supplier', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_supplier_viewing_invalid_url(self):
        """Тест на получение информации о звене сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:supplier', kwargs={'pk': self.vendor2.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/suplier/2/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_supplier_viewing_admin_root_user_no_active(self):
        """Тест на получение информации о звене сети продажи электроники с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:supplier', kwargs={'pk': self.vendor2.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_supplier_viewing_error_because_no_authorization_required(self):
        """Тест на получение информации о звене сети продажи электроники с проверкой на
        получение ошибки доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:supplier', kwargs={'pk': self.vendor2.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class SuppliersUpdateTest(TestBaseData):
    """Класс тестов для эндпоинта редактирования звена сети продаж электроники."""

    @pytest.mark.django_db
    def test_supplier_update_admin_root_successful(self):
        """Тест на редактирование информации о звене сети продажи электроники с успешным запросом от администратора."""

        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.client.force_authenticate(user=self.admin)
        self.updated_data = {'type_point': 'Розничная сеть', 'arrears': 10000, 'supplier': self.vendor1.id}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        distributor = Vendor.objects.filter(name=response.data['name']).first()
        self.assertEqual(distributor.type_point, 'Розничная сеть')
        self.assertEqual(distributor.arrears, 10000)
        self.assertEqual(distributor.supplier, self.vendor1)

    @pytest.mark.django_db
    def test_supplier_update_successful(self):
        """Тест на редактирование информации о звене сети продажи электроники."""

        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.updated_data = {'type_point': 'Розничная сеть'}
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        distributor = Vendor.objects.filter(name=response.data['name']).first()
        self.assertEqual(distributor.type_point, 'Розничная сеть')

    @pytest.mark.django_db
    def test_supplier_update_invalid_pk(self):
        """Тест на редактирование информации о звене сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': randint(1000, 10000)})
        self.updated_data = {'type_point': 'Розничная сеть'}
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_supplier_update_invalid_url(self):
        """Тест на редактирование информации о звене сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.client.force_authenticate(user=self.admin)
        self.updated_data = {'type_point': 'Розничная сеть'}
        response = self.client.patch('/suplier/2/update/', data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_supplier_update_admin_root_user_no_active(self):
        """Тест на редактирование информации о звене сети продажи электроники с проверкой на получение ошибки не
        активности пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.updated_data = {'type_point': 'Розничная сеть'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_supplier_update_error_because_no_authorization_required(self):
        """Тест на редактирование информации о звене сети продажи электроники с проверкой на получение ошибки
        доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.updated_data = {'type_point': 'Розничная сеть'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')

    @pytest.mark.django_db
    def test_supplier_update_admin_root_error_supplier(self):
        """Тест на редактирование информации о звене сети продажи электроники с проверкой на получение ошибки
        валидации по полю "Поставщик"."""

        self.client.force_authenticate(user=self.admin)
        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.updated_data = {'supplier': '1'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Если указано звено сети "Завод", оно не может иметь поставщика. '
                         'Проверьте корректность вводимых данных.'),
                         'Если указано звено сети "Завод", оно не может иметь поставщика. '
                         'Проверьте корректность вводимых данных.')

    @pytest.mark.django_db
    def test_supplier_update_admin_root_error_type_point(self):
        """Тест на редактирование информации о звене сети продажи электроники с проверкой на получение ошибки
        валидации по полю "Поставщик"."""

        self.vendor2.type_point = VendorType.IE
        self.vendor2.supplier = self.vendor1
        self.client.force_authenticate(user=self.admin)
        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.updated_data = {'type_point': 'Завод'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json()[0],
                         'Если указано звено сети "Завод", оно не может иметь поставщика. '
                         'Проверьте корректность вводимых данных.')

    @pytest.mark.django_db
    def test_supplier_update_admin_root_error_arrears_because_type_point(self):
        """Тест на редактирование информации о звене сети продажи электроники с проверкой на получение ошибки
        валидации по полю "Задолженность перед поставщиком" из-за некорректности данных для поля "Тип звена сети
        продаж"."""

        self.client.force_authenticate(user=self.admin)
        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.updated_data = {'arrears': 10000}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Если указано звено сети "Завод", оно не может иметь '
                                                      'положительное значение '
                                                      'в поле "Задолженность перед поставщиком".'),
                         'Если указано звено сети "Завод", оно не может иметь положительное значение в поле '
                         '"Задолженность перед поставщиком".')

    @pytest.mark.django_db
    def test_supplier_update_admin_root_error_arrears_because_supplier(self):
        """Тест на редактирование информации о звене сети продажи электроники с проверкой на получение ошибки
        валидации по полю "Задолженность перед поставщиком" из-за некорректности данных для поля "Поставщик"."""

        self.vendor1.type_point = VendorType.IE
        self.client.force_authenticate(user=self.admin)
        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor1.pk})
        self.updated_data = {'arrears': '10000'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = ArrearsSupplierValidator('arrears', 'supplier')
            validator(self.updated_data)
        self.assertEqual(response.json().get('error', 'Если не указан никакой элемент в поле "Поставщик", '
                                                      '"Задолженность перед поставщиком" не может быть больше нуля.'),
                         'Если не указан никакой элемент в поле "Поставщик", "Задолженность перед поставщиком" не '
                         'может быть больше нуля.')

    @pytest.mark.django_db
    def test_supplier_update_error_arrears_because_permission_denied(self):
        """Тест на редактирование информации о звене сети продажи электроники с проверкой на получение ошибки
        валидации по полю "Задолженность перед поставщиком" из-за отсутствия прав на данное действие."""

        self.vendor2.type_point = VendorType.IE
        self.vendor2.supplier = self.vendor1
        self.url = reverse('electronics_store:update_supplier', kwargs={'pk': self.vendor2.pk})
        self.client.force_authenticate(user=self.user)
        self.updated_data = {'arrears': '10000'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = ArrearsValidator('type_point', 'arrears')
            validator(self.updated_data)
        self.assertEqual(response.json().get('error', 'У Вас не достаточно прав на изменение поля '
                                                      '"Задолженность перед поставщиком".'),
                         'У Вас не достаточно прав на изменение поля "Задолженность перед поставщиком".')


class SuppliersListTest(TestBaseData):
    """Класс тестов для эндпоинта списка звеньев сети продажи электроники."""

    @pytest.mark.django_db
    def test_suppliers_list_admin_root_successful(self):
        """Тест списка звеньев сети продажи электроники с успешным запросом от администратора."""

        self.url = reverse('electronics_store:suppliers')
        self.serializer_vendors = SupplierAdminRootSerializer(Vendor.objects.all(), many=True)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vendor.objects.all().count(), 2)
        self.assertEqual(response.data['results'], self.serializer_vendors.data)

    @pytest.mark.django_db
    def test_suppliers_list_successful(self):
        """Тест списка звеньев сети продажи электроники с успешным запросом."""

        self.url = reverse('electronics_store:suppliers')
        self.serializer_vendors = SupplierSerializer(Vendor.objects.all(), many=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vendor.objects.all().count(), 2)
        self.assertEqual(response.data['results'], self.serializer_vendors.data)

    @pytest.mark.django_db
    def test_suppliers_list_invalid_url(self):
        """Тест списка звеньев сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:suppliers')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/supplierss/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_suppliers_list_admin_root_user_no_active(self):
        """Тест списка звеньев сети продажи электроники с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:suppliers')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_suppliers_list_error_because_no_authorization_required(self):
        """Тест списка звеньев сети продажи электроники с проверкой на получение ошибки
        доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:suppliers')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class SupplierDestroyTest(TestBaseData):
    """Класс тестов для эндпоинта удаления звена сети продажи электроники."""

    @pytest.mark.django_db
    def test_supplier_destroy_admin_root_successful(self):
        """Тест на удаления звена сети продажи электроники с успешным запросом."""

        self.url = reverse('electronics_store:delete_supplier', kwargs={"pk": self.vendor2.pk})
        self.assertEqual(Vendor.objects.all().count(), 2)
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Vendor.objects.all().count(), 1)
        self.serializer_vendor = SupplierAdminRootSerializer(Vendor.objects.all(), many=True)
        self.assertEqual(self.serializer_vendor.data[0]['name'], self.vendor1.name)

    @pytest.mark.django_db
    def test_supplier_destroy_invalid_pk(self):
        """Тест на удаления звена сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:delete_supplier', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_supplier_destroy_invalid_url(self):
        """Тест на удаления звена сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:delete_supplier', kwargs={'pk': self.vendor2.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/suplier/2/delete/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_supplier_destroy_admin_root_user_no_active(self):
        """Тест на удаления звена сети продажи электроники с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:delete_supplier', kwargs={"pk": self.vendor2.pk})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_supplier_destroy_error_because_permission_denied(self):
        """Тест на удаления звена сети продажи электроники с проверкой на получение ошибки валидации из-за
        отсутствия прав на данное действие."""

        self.url = reverse('electronics_store:delete_supplier', kwargs={'pk': self.vendor2.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_supplier_destroy_error_because_no_authorization_required(self):
        """Тест на удаления звена сети продажи электроники с проверкой на получение ошибки
        доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:delete_supplier', kwargs={'pk': self.vendor2.pk})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ContactCreateTest(TestBaseData):
    """Класс тестов для эндпоинта создания контактов для звена сети продажи электроники."""

    @pytest.mark.django_db
    def test_contact_create_successful(self):
        """Тест создания контактов для звена сети продажи электроники с отсутствием ошибок."""

        self.contacts2 = ContactsFactory.create()
        self.contacts2.save()
        self.url = reverse('electronics_store:adding_contact')
        self.client.force_authenticate(user=self.user)
        self.serializer_contact = ContactsSerializer(self.contacts2, many=False)
        form_data = self.serializer_contact.data
        self.contacts2.delete()
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contacts.objects.count(), 2)
        contacts = Contacts.objects.filter(email=response.data['email']).first()
        self.serializer_contact_new = ContactsSerializer(contacts, many=False)
        self.assertEqual(self.serializer_contact_new.data, response.data)

    @pytest.mark.django_db
    def test_contacts_create_invalid_url(self):
        """Тест создания контактов для звена сети продажи электроники с некорректным запросом."""

        self.serializer_contact = ContactsSerializer(self.contacts1, many=False)
        self.url = reverse('electronics_store:adding_contact')
        form_data = self.serializer_contact.data
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/contacts/new/', data=form_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contact_create_admin_root_user_no_active(self):
        """Тест создания контактов для звена сети продажи электроники с проверкой на получение ошибки не активности
        пользователя."""

        self.url = reverse('electronics_store:adding_contact')
        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.serializer_contact = ContactsSerializer(self.contacts1, many=False)
        form_data = self.serializer_contact.data
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_contact_create_error_because_no_authorization_required(self):
        """Тест создания контактов для звена сети продажи электроники с проверкой на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.serializer_contact = ContactsSerializer(self.contacts1, many=False)
        self.url = reverse('electronics_store:adding_contact')
        form_data = self.serializer_contact.data
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ContactsViewingTest(TestBaseData):
    """Класс тестов для эндпоинта просмотра информации о контактах звена сети продаж электроники."""

    @pytest.mark.django_db
    def test_contact_viewing_successful(self):
        """Тест на получение информации о контактах звена сети продажи электроники с успешным запросом."""

        self.serializer_contacts = ContactsSerializer(self.contacts1, many=False)
        self.url = reverse('electronics_store:contact', kwargs={'pk': self.contacts1.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.serializer_contacts.data)

    @pytest.mark.django_db
    def test_contact_viewing_invalid_pk(self):
        """Тест на получение информации о контактах звена сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:contact', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contacts_viewing_invalid_url(self):
        """Тест на получение информации о контактах звена сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:contact', kwargs={'pk': self.contacts1.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/contacts/1/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contact_viewing_admin_root_user_no_active(self):
        """Тест на получение информации о контактах звена сети продажи электроники с проверкой на получение ошибки не
        активности пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:contact', kwargs={'pk': self.contacts1.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_contact_viewing_error_because_no_authorization_required(self):
        """Тест на получение информации о контактах звена сети продажи электроники о продукте с проверкой на
        получение ошибки доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:contact', kwargs={'pk': self.contacts1.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ContactsUpdateTest(TestBaseData):
    """Класс тестов для эндпоинта редактирования информации о контактах звена сети продаж электроники."""

    @pytest.mark.django_db
    def test_contact_update_successful(self):
        """Тест редактирования информации о контактах звена сети продажи электроники."""

        self.serializer_contact = ContactsSerializer(self.contacts1, many=False)
        self.url = reverse('electronics_store:update_contact', kwargs={'pk': self.contacts1.pk})
        self.client.force_authenticate(user=self.user)
        self.updated_data = {'email': 'test.email.company@mail.ru'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        contact = Contacts.objects.filter(email=response.data['email']).first()
        self.assertEqual(contact.email, 'test.email.company@mail.ru')

    @pytest.mark.django_db
    def test_contact_update_invalid_pk(self):
        """Тест на редактирование информации о контактах звена сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:update_contact', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.user)
        self.updated_data = {'email': 'test.email.company@mail.ru'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contacts_update_invalid_url(self):
        """Тест на редактирование информации о контактах звена сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:update_contact', kwargs={'pk': self.contacts1.pk})
        self.client.force_authenticate(user=self.admin)
        self.updated_data = {'email': 'test.email.company@mail.ru'}
        response = self.client.patch('/contacts/1/update/', data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contact_update_admin_root_user_no_active(self):
        """Тест редактирования информации о контактах звена сети продажи электроники с проверкой на получение ошибки не
        активности пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:update_contact', kwargs={'pk': self.contacts1.pk})
        self.updated_data = {'email': 'test.email.company@mail.ru'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_contact_update_error_because_no_authorization_required(self):
        """Тест редактирования информации о контактах звена сети продажи электроники с проверкой на получение ошибки
        доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:update_contact', kwargs={'pk': self.contacts1.pk})
        self.updated_data = {'email': 'test.email.company@mail.ru'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ContactsListTest(TestBaseData):
    """Класс тестов для эндпоинта списка информации о контактах звеньев сети продажи электроники."""

    @pytest.mark.django_db
    def test_contacts_list_successful(self):
        """Тест списка информации о контактах звеньев сети продажи электроники с успешным запросом."""

        self.url = reverse('electronics_store:contacts')
        self.serializer_contacts = ContactsSerializer(Contacts.objects.all(), many=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contacts.objects.all().count(), 1)
        self.assertEqual(response.data['results'], self.serializer_contacts.data)

    @pytest.mark.django_db
    def test_contacts_list_invalid_url(self):
        """Тест списка информации о контактах звеньев сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:contacts')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/contactss/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contacts_list_admin_root_user_no_active(self):
        """Тест списка информации о контактах звеньев сети продажи электроники с проверкой на получение ошибки не
        активности пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:contacts')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_contacts_list_error_because_no_authorization_required(self):
        """Тест списка информации о контактах звеньев сети продажи электроники с проверкой на получение ошибки
        доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:contacts')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ContactsDestroyTest(TestBaseData):
    """Класс тестов для эндпоинта удаления информации о контактах звена сети продажи электроники."""

    @pytest.mark.django_db
    def test_contact_destroy_admin_root_successful(self):
        """Тест на удаления информации о контактах звена сети продажи электроники с успешным запросом."""

        self.contacts2 = ContactsFactory.create()
        self.contacts2.save()
        self.url = reverse('electronics_store:delete_contact', kwargs={"pk": self.contacts1.pk})
        self.assertEqual(Contacts.objects.all().count(), 2)
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Contacts.objects.all().count(), 1)
        self.serializer_contacts = ContactsSerializer(Contacts.objects.all(), many=True)
        self.assertEqual(self.serializer_contacts.data[0]['email'], self.contacts2.email)

    @pytest.mark.django_db
    def test_contact_destroy_invalid_pk(self):
        """Тест на удаления информации о контактах звена сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:delete_contact', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contacts_destroy_invalid_url(self):
        """Тест на удаления информации о контактах звеньев сети продажи электроники с некорректным запросом."""

        self.url = reverse('electronics_store:delete_contact', kwargs={"pk": self.contacts1.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/contacts/1/delete/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_contact_destroy_admin_root_user_no_active(self):
        """Тест на удаления информации о контактах звена сети продажи электроники с проверкой на получение ошибки не
        активности пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:delete_contact', kwargs={"pk": self.contacts1.pk})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_contact_destroy_error_because_permission_denied(self):
        """Тест на удаления информации о контактах звена сети продажи электроники с проверкой на получение ошибки
        валидации из-за отсутствия прав на данное действие."""

        self.url = reverse('electronics_store:delete_contact', kwargs={'pk': self.contacts1.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'У вас недостаточно прав для выполнения данного действия.'),
                         'У вас недостаточно прав для выполнения данного действия.')

    @pytest.mark.django_db
    def test_contact_destroy_error_because_no_authorization_required(self):
        """Тест на удаления информации о контактах звена сети продажи электроники с проверкой на получение ошибки
        доступа из-за отсутствия авторизации."""

        self.url = reverse('electronics_store:delete_contact', kwargs={'pk': self.contacts1.pk})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ProductCreateTest(TestBaseData):
    """Класс тестов для эндпоинта создания продуктов."""

    @pytest.mark.django_db
    def test_product_create_successful(self):
        """Тест создания продуктов с отсутствием ошибок."""

        self.url = reverse('electronics_store:adding_product')
        self.client.force_authenticate(user=self.user)
        self.serializer_product = ProductSerializer(self.product3, many=False)
        form_data = self.serializer_product.data
        self.product3.delete()
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 3)
        product = Product.objects.filter(model=response.data['model']).first()
        self.serializer_product_new = ProductSerializer(product, many=False)
        self.assertEqual(self.serializer_product_new.data, response.data)

    @pytest.mark.django_db
    def test_product_create_invalid_url(self):
        """Тест создания продуктов с некорректным запросом."""

        self.serializer_product = ProductSerializer(self.product3, many=False)
        form_data = self.serializer_product.data
        self.url = reverse('electronics_store:adding_product')
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/products/new/', data=form_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_product_create_admin_root_user_no_active(self):
        """Тест создания продуктов с проверкой на получение ошибки не активности
        пользователя."""

        self.url = reverse('electronics_store:adding_product')
        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.serializer_product = ProductSerializer(self.product3, many=False)
        form_data = self.serializer_product.data
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_product_create_error_because_no_authorization_required(self):
        """Тест создания продуктов с проверкой на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.serializer_product = ProductSerializer(self.product3, many=False)
        self.url = reverse('electronics_store:adding_product')
        form_data = self.serializer_product.data
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ProductViewingTest(TestBaseData):
    """Класс тестов для эндпоинта просмотра информации о продукте."""

    @pytest.mark.django_db
    def test_product_viewing_successful(self):
        """Тест на получение информации о продукте с успешным запросом."""

        self.serializer_product = ProductSerializer(self.product3, many=False)
        self.url = reverse('electronics_store:product', kwargs={'pk': self.product3.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.serializer_product.data)

    @pytest.mark.django_db
    def test_product_viewing_invalid_pk(self):
        """Тест на получение информации о продукте с некорректным запросом."""

        self.url = reverse('electronics_store:product', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_product_viewing_invalid_url(self):
        """Тест на получение информации о продукте с некорректным запросом."""

        self.url = reverse('electronics_store:product', kwargs={'pk': self.product3.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/products/3/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_product_viewing_admin_root_user_no_active(self):
        """Тест на получение информации о продукте с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:product', kwargs={'pk': self.product3.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_product_viewing_error_because_no_authorization_required(self):
        """Тест на получение информации о продукте с проверкой на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.url = reverse('electronics_store:product', kwargs={'pk': self.product3.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ProductUpdateTest(TestBaseData):
    """Класс тестов для эндпоинта редактирования информации о продукте."""

    @pytest.mark.django_db
    def test_product_update_successful(self):
        """Тест редактирования информации о продукте с успешным запросом."""

        self.serializer_product = ProductSerializer(self.product3, many=False)
        self.url = reverse('electronics_store:update_product', kwargs={'pk': self.product3.pk})
        self.client.force_authenticate(user=self.user)
        self.updated_data = {'name': 'Название продукта для тестов приложения'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        product = Product.objects.filter(name=response.data['name']).first()
        self.assertEqual(product.name, 'Название продукта для тестов приложения')

    @pytest.mark.django_db
    def test_product_update_invalid_pk(self):
        """Тест на редактирование информации о продукте с некорректным запросом."""

        self.url = reverse('electronics_store:update_product', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.user)
        self.updated_data = {'name': 'Название продукта для тестов приложения'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_product_update_invalid_url(self):
        """Тест на редактирование информации о продукте с некорректным запросом."""

        self.url = reverse('electronics_store:update_product', kwargs={'pk': self.product3.pk})
        self.client.force_authenticate(user=self.admin)
        self.updated_data = {'name': 'Название продукта для тестов приложения'}
        response = self.client.patch('/products/3/update/', data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_product_update_admin_root_user_no_active(self):
        """Тест редактирования информации о продукте с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:update_product', kwargs={'pk': self.product3.pk})
        self.updated_data = {'name': 'Название продукта для тестов приложения'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_product_update_error_because_no_authorization_required(self):
        """Тест редактирования информации о продукте с проверкой на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.url = reverse('electronics_store:update_product', kwargs={'pk': self.product3.pk})
        self.updated_data = {'name': 'Название продукта для тестов приложения'}
        response = self.client.patch(self.url, data=self.updated_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ProductsListTest(TestBaseData):
    """Класс тестов для эндпоинта списка информации о продуктах."""

    @pytest.mark.django_db
    def test_products_list_successful(self):
        """Тест списка информации о продуктах с успешным запросом."""

        self.url = reverse('electronics_store:products')
        self.serializer_products = ProductSerializer(Product.objects.all(), many=True)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.all().count(), 3)
        self.assertEqual(response.data['results'], self.serializer_products.data)

    @pytest.mark.django_db
    def test_products_list_invalid_url(self):
        """Тест списка информации о продуктах с некорректным запросом."""

        self.url = reverse('electronics_store:products')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/productss/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_products_list_admin_root_user_no_active(self):
        """Тест списка информации о продуктах с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:products')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_products_list_error_because_no_authorization_required(self):
        """Тест списка информации о продуктах с проверкой на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.url = reverse('electronics_store:products')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')


class ProductDestroyTest(TestBaseData):
    """Класс тестов для эндпоинта удаления информации о продукте."""

    @pytest.mark.django_db
    def test_product_destroy_admin_root_successful(self):
        """Тест на удаление информации о продукте с успешным запросом."""

        self.product4 = ProductFactory.create()
        self.product4.save()
        self.url = reverse('electronics_store:delete_product', kwargs={"pk": self.product4.pk})
        self.assertEqual(Product.objects.all().count(), 4)
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Product.objects.all().count(), 3)

    @pytest.mark.django_db
    def test_product_destroy_invalid_pk(self):
        """Тест на удаление информации о продукте с некорректным запросом."""

        self.url = reverse('electronics_store:delete_product', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_product_destroy_invalid_url(self):
        """Тест на удаление информации о продукте с некорректным запросом."""

        self.url = reverse('electronics_store:delete_product', kwargs={'pk': self.product3.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/products/3/delete/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_product_destroy_admin_root_user_no_active(self):
        """Тест на удаления информации о продукте с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('electronics_store:delete_product', kwargs={"pk": self.product3.pk})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_product_destroy_error_because_no_authorization_required(self):
        """Тест на удаление информации о продукте с проверкой на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.url = reverse('electronics_store:delete_product', kwargs={'pk': self.product3.pk})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')

    @pytest.mark.django_db
    def test_product_destroy_error_because_permission_denied(self):
        """Тест на удаление информации о продукте с проверкой на получение ошибки валидации из-за
        отсутствия прав на данное действие."""

        self.url = reverse('electronics_store:delete_product', kwargs={'pk': self.product3.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'У вас недостаточно прав для выполнения данного действия.'),
                         'У вас недостаточно прав для выполнения данного действия.')
