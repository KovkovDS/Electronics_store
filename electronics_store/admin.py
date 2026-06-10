from django.contrib import admin
from django.utils.html import format_html
from electronics_store.models import Vendor, Contacts, Product


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """Класс для управления экземплярами модели "Пользователь" через административную панель."""
    list_display = ('name', 'type_point', 'display_supplier', 'arrears', 'display_contacts_country',
                    'display_contacts_city', 'display_contacts_street', 'display_contacts_house',
                    'display_product_name', 'display_product_model', 'release_date')
    list_filter = ('contacts__city',)
    search_fields = ('name', 'type_point', 'display_supplier', 'arrears', 'display_contacts_country',
                     'display_contacts_city', 'display_contacts_street', 'display_contacts_house',
                     'display_product_name', 'display_product_model', 'release_date')
    actions = ["clear_arrears"]

    @admin.display(description="Страна")
    def display_contacts_country(self, obj):
        """Метод для вывода страны в контактах Поставщика."""
        return obj.contacts.country

    @admin.display(description="Город")
    def display_contacts_city(self, obj):
        """Метод для вывода города в контактах Поставщика."""
        return obj.contacts.city

    @admin.display(description="Улица")
    def display_contacts_street(self, obj):
        """Метод для вывода улицы в контактах Поставщика."""
        return obj.contacts.street

    @admin.display(description="Номер дома")
    def display_contacts_house(self, obj):
        """Метод для вывода улицы в контактах Поставщика."""
        return obj.contacts.house

    @admin.display(description="Поставщик")
    def display_supplier(self, obj):
        """Метод для вывода информации по Поставщику для конкретного звена сети продаж."""
        if obj.supplier:
            return format_html(
                '<a href="{}">{}</a>',
                f"/admin/electronics_store/vendor/{obj.supplier.id}/change/",
                obj.supplier.name,
            )
        return "-"

    @admin.display(description="Наименование продукта")
    def display_product_name(self, obj):
        """Метод для вывода названий продуктов, связанных с Поставщиком."""
        if obj.products:
            for product in obj.products.all():
                return format_html(
                    '<a href="{}">{}</a>',
                    f"/admin/electronics_store/product/{product.id}/change/",
                    product.name
                    )
        return "-"

    @admin.display(description="Модель продукта")
    def display_product_model(self, obj):
        """Метод для вывода моделей продуктов, связанных с Поставщиком."""
        if obj.products:
            for product in obj.products.all():
                return format_html(
                    '<a href="{}">{}</a>',
                    f"/admin/electronics_store/product/{product.id}/change/",
                    product.model
                )
        return "-"

    @admin.action(description="Очистить задолженность у выбранных объектов")
    def clear_arrears(self, request, queryset):
        """Метод для обнуления поле "Задолженность перед поставщиком" для конкретного звена сети продаж."""
        updated = queryset.update(arrears=0)
        self.message_user(request, f"Задолженность очищена у {updated} объектов")


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    """Класс для управления экземплярами модели "Пользователь" через административную панель."""
    list_display = ('email', 'country', 'city', 'street', 'house')
    list_filter = ('email', 'country', 'city', 'street', 'house')
    search_fields = ('email', 'country', 'city', 'street', 'house')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Класс для управления экземплярами модели "Пользователь" через административную панель."""
    list_display = ('name', 'model', 'release_date')
    list_filter = ('name', 'model', 'release_date')
    search_fields = ('name', 'model', 'release_date')
