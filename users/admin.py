from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс для управления экземплярами модели "Пользователь" через административную панель."""
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'is_active', 'updated_at')
    list_filter = ('email', 'first_name', 'last_name', 'phone_number', 'city')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number', 'city')
