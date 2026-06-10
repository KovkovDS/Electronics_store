from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUserManager(BaseUserManager):
    """Класс менеджера для создания объектов модели "Пользователь"."""

    def create_user(self, email, password=None, **extra_fields):
        """Метод создания объекта "пользователь" модели "Пользователь"."""

        if not email:
            raise ValueError('Адрес электронной почты должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Метод создания объекта "суперпользователь" модели "Пользователь"."""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Класс модели "Пользователь"."""

    email = models.EmailField(unique=True, verbose_name='Адрес электронной почты')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Номер телефона')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    is_active = models.BooleanField(default=True, verbose_name="Активность сотрудника")
    create_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    objects = CustomUserManager()

    def __str__(self):
        """Метод для описания человеко читаемого вида модели "Пользователь"."""

        return f'{self.id}, {self.email}'

    class Meta:
        """Класс для изменения поведения полей модели "Пользователь"."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email', 'phone_number', 'is_active', 'updated_at']
