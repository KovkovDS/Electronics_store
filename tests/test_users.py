from random import randint
import pytest
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from factories import UserFactory, UserAdminFactory
from users.models import User
from users.serializer import CreateProfileSerializer, ProfileSerializer, ProfileUserSerializer, ProfileViewingSerializer
from users.validators import PhoneNumberValidator


class TestBaseData(APITestCase):
    """Класс с первичными данными для тестов эндпоинтов для модели "Поставщик"."""

    def setUp(self):
        """ Метод класса с начальными данными для тестов."""
        self.admin = UserAdminFactory.create()
        self.admin.save()
        self.user = UserFactory.create()
        self.user.save()


class ProfileCreateTest(TestBaseData):
    """Класс тестов для эндпоинта регистрации или создания пользователя приложения."""

    @pytest.mark.django_db
    def test_profile_create_successful(self):
        """Тест регистрации пользователя с отсутствием ошибок."""

        self.assertEqual(User.objects.count(), 2)
        self.url = reverse('users:registration')
        self.serializer_profile = CreateProfileSerializer(UserFactory(), many=False)
        form_data = self.serializer_profile.data
        form_data['password'] = 'test2345'
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 3)
        user = User.objects.filter(last_name=response.data['last_name']).first()
        self.serializer_profile_new = CreateProfileSerializer(user, many=False)
        self.assertEqual(self.serializer_profile_new.data, response.data)

    @pytest.mark.django_db
    def test_profile_create_admin_root_successful(self):
        """Тест регистрации пользователя с отсутствием ошибок."""

        self.client.force_authenticate(user=self.admin)
        self.assertEqual(User.objects.count(), 2)
        self.url = reverse('users:registration')
        self.serializer_profile = ProfileSerializer(UserAdminFactory(), many=False, read_only=True)
        form_data = self.serializer_profile.data
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 3)
        user = User.objects.filter(last_name=response.data['last_name']).first()
        self.serializer_profile_new = ProfileSerializer(user, many=False)
        self.assertEqual(self.serializer_profile_new.data, response.data)

    @pytest.mark.django_db
    def test_profile_create_user_admin_error_because_permission_denied(self):
        """Тест регистрации пользователя с получением ошибки из-за отсутствия прав на данное действие."""

        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:registration')
        self.serializer_profile = ProfileSerializer(UserAdminFactory(), many=False, read_only=True)
        form_data = self.serializer_profile.data
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 403)

    @pytest.mark.django_db
    def test_profile_create_invalid_url(self):
        """Тест регистрации пользователя с некорректным запросом."""

        self.url = reverse('users:registration')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('regestration/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_profile_create_error_no_correct_phone_number(self):
        """Тест регистрации пользователя с проверкой на получение ошибки
        валидации по полю "Номер телефона"."""

        self.url = reverse('users:registration')
        self.serializer_profile = CreateProfileSerializer(UserFactory(), many=False, read_only=True)
        form_data = self.serializer_profile.data
        form_data['phone_number'] = '+71234567890'
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = PhoneNumberValidator('phone_number')
            validator(form_data)
        self.assertEqual(response.json().get('error', 'Некорректный формат поля "Номер телефона".'),
                         'Некорректный формат поля "Номер телефона".'
                         )

    @pytest.mark.django_db
    def test_profile_create_error_phone_number_required(self):
        """Тест регистрации пользователя с проверкой на получение ошибки
        валидации по полю "Номер телефона"."""

        self.url = reverse('users:registration')
        self.serializer_profile = CreateProfileSerializer(UserFactory(), many=False, read_only=True)
        form_data = self.serializer_profile.data
        form_data['phone_number'] = None
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = PhoneNumberValidator('phone_number')
            validator(form_data)
        self.assertEqual(response.json().get('error', 'Обязательное поле "Номер телефона" не заполнено. Укажите '
                                                      'корректную информацию.'),
                         'Обязательное поле "Номер телефона" не заполнено. Укажите корректную информацию.'
                         )

    @pytest.mark.django_db
    def test_profile_create_error_email_required(self):
        """Тест регистрации пользователя с проверкой на получение ошибки
        валидации по полю "Адрес электронной почты"."""

        self.url = reverse('users:registration')
        self.serializer_profile = CreateProfileSerializer(UserFactory(), many=False, read_only=True)
        form_data = self.serializer_profile.data
        form_data['email'] = None
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Это поле не может быть пустым.'),
                         'Это поле не может быть пустым.'
                         )

    @pytest.mark.django_db
    def test_profile_create_error_email_need_unique(self):
        """Тест регистрации пользователя с проверкой на получение ошибки
        уникальности по полю "Адрес электронной почты"."""

        self.user_test = UserFactory.create()
        self.user_test.save()
        self.serializer_profile = ProfileUserSerializer(self.user_test, many=False)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:registration')
        form_data = self.serializer_profile.data
        form_data['email'] = self.serializer_profile.data['email']
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Это поле не может быть пустым.'),
                         'Это поле не может быть пустым.'
                         )

    @pytest.mark.django_db
    def test_profile_create_error_password_required(self):
        """Тест регистрации пользователя с проверкой на получение ошибки
        валидации по полю "Пароль"."""

        self.url = reverse('users:registration')
        self.serializer_profile = CreateProfileSerializer(UserFactory(), many=False, read_only=True)
        form_data = self.serializer_profile.data
        form_data['password'] = None
        response = self.client.post(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Это поле не может быть пустым.'),
                         'Это поле не может быть пустым.'
                         )


class ProfileViewingTest(TestBaseData):
    """Класс тестов для эндпоинта просмотра информации о пользователе приложения."""

    @pytest.mark.django_db
    def test_profile_viewing_owner_profile_successful(self):
        """Тест просмотра информации о пользователе владельцем аккаунта с отсутствием ошибок."""

        self.serializer_profile = ProfileUserSerializer(self.user, many=False)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:profile', kwargs={'pk': self.user.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.serializer_profile.data)

    @pytest.mark.django_db
    def test_profile_viewing_successful(self):
        """Тест просмотра информации о пользователе с отсутствием ошибок."""

        self.user_test = UserFactory.create()
        self.user_test.save()
        self.serializer_profile = ProfileViewingSerializer(self.user, many=False)
        self.client.force_authenticate(user=self.user_test)
        self.url = reverse('users:profile', kwargs={'pk': self.user.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.serializer_profile.data)

    @pytest.mark.django_db
    def test_profile_viewing_admin_root_successful(self):
        """Тест просмотра информации о пользователе администратором с отсутствием ошибок."""

        self.serializer_profile = ProfileSerializer(self.admin, many=False, read_only=True)
        self.client.force_authenticate(user=self.admin)
        self.url = reverse('users:profile', kwargs={'pk': self.admin.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.serializer_profile.data)

    @pytest.mark.django_db
    def test_profile_viewing_error_because_no_authorization_required(self):
        """Тест просмотра информации о пользователе на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.serializer_profile = ProfileSerializer(UserAdminFactory(), many=False, read_only=True)
        self.url = reverse('users:profile', kwargs={'pk': self.user.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_profile_viewing_invalid_pk(self):
        """Тест просмотра информации о пользователе с некорректным запросом."""

        self.url = reverse('users:profile', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_profile_viewing_invalid_url(self):
        """Тест просмотра информации о пользователе с некорректным запросом."""

        self.url = reverse('users:profile', kwargs={'pk': self.user.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('profil/2/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_profile_viewing_admin_root_user_no_active(self):
        """Тест просмотра информации о пользователе на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('users:profile', kwargs={'pk': self.user.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)


class ProfileUpdateTest(TestBaseData):
    """Класс тестов для эндпоинта редактирования информации о пользователе приложения."""

    @pytest.mark.django_db
    def test_profile_update_successful(self):
        """Тест редактирования информации о пользователе с отсутствием ошибок."""

        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:update_profile', kwargs={'pk': self.user.pk})
        form_data = {'password': 'test12345'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.filter(last_name=response.data['last_name']).first()
        self.assertEqual(user.password, response.data['password'])

    @pytest.mark.django_db
    def test_profile_update_admin_root_successful(self):
        """Тест редактирования информации о пользователе с отсутствием ошибок."""

        self.client.force_authenticate(user=self.admin)
        self.url = reverse('users:update_profile', kwargs={'pk': self.admin.pk})
        form_data = {'password': 'admin12345'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 200)
        user = User.objects.filter(last_name=response.data['last_name']).first()
        self.assertEqual(user.password, response.data['password'])

    @pytest.mark.django_db
    def test_profile_update_user_admin_error_because_permission_denied(self):
        """Тест редактирования информации о пользователе с получением ошибки из-за
        отсутствия прав на данное действие."""

        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:update_profile', kwargs={'pk': self.admin.pk})
        form_data = {'last_name': 'Testov'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('error', 'У вас недостаточно прав для выполнения данного действия.'),
                         'У вас недостаточно прав для выполнения данного действия.'
                         )

    @pytest.mark.django_db
    def test_profile_update_user_error_because_permission_denied(self):
        """Тест редактирования информации о пользователе с получением ошибки из-за
        отсутствия прав на данное действие."""

        self.user_test = UserFactory.create()
        self.user_test.save()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:update_profile', kwargs={'pk': self.user_test.pk})
        form_data = {'last_name': 'Testov'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get('error', 'У вас недостаточно прав для выполнения данного действия.'),
                         'У вас недостаточно прав для выполнения данного действия.'
                         )

    @pytest.mark.django_db
    def test_profile_update_user_error_because_no_authorization_required(self):
        """Тест редактирования информации о пользователе с проверкой на получение ошибки доступа из-за отсутствия
        авторизации."""

        self.url = reverse('users:update_profile', kwargs={'pk': self.user.pk})
        form_data = {'last_name': 'Testov'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.'
                         )

    @pytest.mark.django_db
    def test_profile_update_invalid_pk(self):
        """Тест просмотра информации о пользователе с некорректным запросом."""

        self.url = reverse('users:update_profile', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        form_data = {'password': 'admin12345'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_profile_update_invalid_url(self):
        """Тест редактирования информации о пользователе с некорректным запросом."""

        self.client.force_authenticate(user=self.admin)
        self.url = reverse('users:update_profile', kwargs={'pk': self.admin.pk})
        form_data = {'password': 'admin12345'}
        response = self.client.patch('profil/1/update/', data=form_data, format='json')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_profile_update_error_no_correct_phone_number(self):
        """Тест редактирования информации о пользователе на получение ошибки
        валидации по полю "Номер телефона"."""

        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:update_profile', kwargs={'pk': self.user.pk})
        form_data = {'phone_number': '+71234567890'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        with self.assertRaises(ValidationError):
            validator = PhoneNumberValidator('phone_number')
            validator(form_data)
        self.assertEqual(response.json().get('error', 'Некорректный формат поля "Номер телефона".'),
                         'Некорректный формат поля "Номер телефона".'
                         )

    @pytest.mark.django_db
    def test_profile_update_error_email_required(self):
        """Тест редактирования информации о пользователе с проверкой на получение ошибки
        валидации по полю "Адрес электронной почты"."""

        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:update_profile', kwargs={'pk': self.user.pk})
        form_data = {'email': None}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Это поле не может быть пустым.'),
                         'Это поле не может быть пустым.'
                         )

    @pytest.mark.django_db
    def test_profile_update_error_email_need_unique(self):
        """Тест редактирования информации о пользователе с проверкой на получение ошибки
        уникальности по полю "Адрес электронной почты"."""

        self.user_test = UserFactory.create()
        self.user_test.save()
        serializer_profile = ProfileUserSerializer(self.user_test, many=False)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:update_profile', kwargs={'pk': self.user.pk})
        form_data = {'email': serializer_profile.data['email']}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Пользователь с таким Адрес электронной почты уже существует.'),
                         'Пользователь с таким Адрес электронной почты уже существует.'
                         )

    @pytest.mark.django_db
    def test_profile_update_error_password_required(self):
        """Тест редактирования информации о пользователе с проверкой на получение ошибки
        валидации по полю "Пароль"."""

        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:update_profile', kwargs={'pk': self.user.pk})
        form_data = {'email': None}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertRaises(ValidationError)
        self.assertEqual(response.json().get('error', 'Это поле не может быть пустым.'),
                         'Это поле не может быть пустым.'
                         )

    @pytest.mark.django_db
    def test_profile_update_admin_root_user_no_active(self):
        """Тест редактирования информации о пользователе с проверкой на получение ошибки не активности
        пользователя."""

        self.url = reverse('users:update_profile', kwargs={'pk': self.user.pk})
        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        form_data = {'last_name': 'Testov'}
        response = self.client.patch(self.url, data=form_data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)


class ListProfilesTest(TestBaseData):
    """Класс тестов для эндпоинта просмотра списка пользователей приложения."""

    @pytest.mark.django_db
    def test_list_profiles_successful(self):
        """Тест просмотра списка пользователей с отсутствием ошибок."""

        self.serializer_profile = ProfileViewingSerializer(User.objects.all(), many=True)
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:profiles')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], self.serializer_profile.data)

    @pytest.mark.django_db
    def test_list_profiles_admin_root_successful(self):
        """Тест просмотра списка пользователей администратором с отсутствием ошибок."""

        self.serializer_profile = ProfileSerializer(User.objects.all(), many=True)
        self.client.force_authenticate(user=self.admin)
        self.url = reverse('users:profiles')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], self.serializer_profile.data)

    @pytest.mark.django_db
    def test_list_profiles_error_because_no_authorization_required(self):
        """Тест просмотра списка пользователей на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.url = reverse('users:profiles')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')

    @pytest.mark.django_db
    def test_list_profiles_invalid_url(self):
        """Тест просмотра списка пользователей с некорректным запросом."""

        self.url = reverse('users:profiles')
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('profiles/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_list_profiles_admin_root_user_no_active(self):
        """Тест просмотра списка пользователей на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('users:profiles')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)


class UserDestroyTest(TestBaseData):
    """Класс тестов для эндпоинта удаления пользователя приложения."""

    def test_user_destroy_admin_root_successful(self):
        """Тест на удаления пользователя с успешным запросом."""

        self.url = reverse('users:delete_profile', kwargs={"pk": self.user.pk})
        self.assertEqual(User.objects.all().count(), 2)
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.all().count(), 1)
        self.serializer_vendor = ProfileSerializer(User.objects.all(), many=True)
        self.assertEqual(self.serializer_vendor.data[0]['email'], self.admin.email)

    @pytest.mark.django_db
    def test_user_destroy_invalid_pk(self):
        """Тест на удаления пользователя с некорректным запросом."""

        self.url = reverse('users:delete_profile', kwargs={'pk': randint(1000, 10000)})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_user_destroy_invalid_url(self):
        """Тест на удаления пользователя с некорректным запросом."""

        self.url = reverse('users:delete_profile', kwargs={'pk': self.user.pk})
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/profiles/2/delete/')
        self.assertEqual(response.status_code, 404)

    @pytest.mark.django_db
    def test_user_destroy_admin_root_user_no_active(self):
        """Тест на удаления пользователя с проверкой на получение ошибки не активности
        пользователя."""

        self.test_user = User.objects.create_user(email='testuser@ya,ru', password='password123', is_active=False,
                                                  is_staff=True, is_superuser=True)
        self.client.login(email='testuser@ya,ru', password='password123')
        self.url = reverse('users:delete_profile', kwargs={"pk": self.user.pk})
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)

    @pytest.mark.django_db
    def test_user_destroy_error_because_permission_denied(self):
        """Тест на удаления пользователя с проверкой на получение ошибки из-за
        отсутствия прав на данное действие."""

        self.url = reverse('users:delete_profile', kwargs={'pk': self.user.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'У вас недостаточно прав для выполнения данного действия.'),
                         'У вас недостаточно прав для выполнения данного действия.')

    @pytest.mark.django_db
    def test_user_destroy_error_because_no_authorization_required(self):
        """Тест на удаления пользователя на получение ошибки доступа из-за
        отсутствия авторизации."""

        self.url = reverse('users:delete_profile', kwargs={'pk': self.user.pk})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertRaises(PermissionError)
        self.assertEqual(response.json().get('error', 'Учетные данные не были предоставлены.'),
                         'Учетные данные не были предоставлены.')
