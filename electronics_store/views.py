from rest_framework import generics, status, serializers
from django_filters import rest_framework as filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from electronics_store.models import Vendor, Contacts, Product
from electronics_store.paginators import SuppliersPaginator, ContactsPaginator, ProductsPaginator
from electronics_store.serializers import ContactsSerializer, ProductSerializer, SupplierSerializer, \
    SupplierAdminRootSerializer
from users.permissions import IsUserActive


class SupplierCreateAPIView(generics.CreateAPIView):
    """Класс представления вида Generic для эндпоинта создания привычки."""

    serializer_class = SupplierAdminRootSerializer
    permission_classes = [IsAuthenticated, IsUserActive]


class SupplierUpdateAPIView(generics.UpdateAPIView):
    """Класс представления вида Generic для эндпоинта изменения поставщика."""

    serializer_class = SupplierSerializer
    queryset = Vendor.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive]

    def get_serializer_class(self):
        """Метод получения сериализатора в соответствии с запросом."""

        if self.request.user.is_superuser:
            return SupplierAdminRootSerializer
        return SupplierSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'type_point' in request.data:
            if request.data['type_point'] == 'Завод' and instance.supplier is None:
                raise serializers.ValidationError('Если указано звено сети "Завод", оно не может иметь поставщика. '
                                                  'Проверьте корректность вводимых данных.'
                                                  )
        elif 'supplier' in request.data:
            if request.data['supplier'] is None and instance.type_point == 'Завод':
                raise serializers.ValidationError('Если указано звено сети "Завод", оно не может иметь поставщика. '
                                                  'Проверьте корректность вводимых данных.'
                                                  )
        elif 'supplier' and 'type_point' in request.data:
            if request.data['supplier'] is None and request.data['type_point'] == 'Завод':
                raise serializers.ValidationError('Если указано звено сети "Завод", оно не может иметь поставщика. '
                                                  'Проверьте корректность вводимых данных.'
                                                  )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupplierFilterCountry(filters.FilterSet):
    """Класс для фильтрации поставщиков по стране."""

    country = filters.CharFilter(field_name='contacts__country', lookup_expr='iexact')

    class Meta:
        """Метод для изменения запроса к базе данных по объектам модели "Поставщик"."""
        model = Vendor
        fields = ['country']


class SuppliersListAPIView(generics.ListAPIView):
    """Класс представления вида Generic для эндпоинта списка звеньев продаж."""

    serializer_class = SupplierSerializer
    queryset = Vendor.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SupplierFilterCountry
    pagination_class = SuppliersPaginator
    permission_classes = [IsAuthenticated, IsUserActive]

    def get_serializer_class(self):
        """Метод получения сериализатора в соответствии с запросом."""

        if self.request.user.is_superuser:
            return SupplierAdminRootSerializer
        return SupplierSerializer


class SupplierViewingAPIView(generics.RetrieveAPIView):
    """Класс представления вида Generic для эндпоинта просмотра привычки."""

    serializer_class = SupplierSerializer
    queryset = Vendor.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive]

    def get_serializer_class(self):
        """Метод получения сериализатора в соответствии с запросом."""

        if self.request.user.is_superuser:
            return SupplierAdminRootSerializer
        return SupplierSerializer


class SupplierDestroyAPIView(generics.DestroyAPIView):
    """Класс представления вида Generic для эндпоинта удаления привычки."""

    queryset = Vendor.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive, IsAdminUser]


class ContactCreateAPIView(generics.CreateAPIView):
    """Класс представления вида Generic для эндпоинта создания привычки."""

    serializer_class = ContactsSerializer
    permission_classes = [IsAuthenticated, IsUserActive]


class ContactUpdateAPIView(generics.UpdateAPIView):
    """Класс представления вида Generic для эндпоинта изменения поставщика."""

    serializer_class = ContactsSerializer
    queryset = Contacts.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive]


class ContactsListAPIView(generics.ListAPIView):
    """Класс представления вида Generic для эндпоинта списка звеньев продаж."""

    serializer_class = ContactsSerializer
    queryset = Contacts.objects.all()
    pagination_class = ContactsPaginator
    permission_classes = [IsAuthenticated, IsUserActive]


class ContactViewingAPIView(generics.RetrieveAPIView):
    """Класс представления вида Generic для эндпоинта просмотра привычки."""

    serializer_class = ContactsSerializer
    queryset = Contacts.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive]


class ContactDestroyAPIView(generics.DestroyAPIView):
    """Класс представления вида Generic для эндпоинта удаления привычки."""

    queryset = Contacts.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive, IsAdminUser]


class ProductCreateAPIView(generics.CreateAPIView):
    """Класс представления вида Generic для эндпоинта создания привычки."""

    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsUserActive]


class ProductUpdateAPIView(generics.UpdateAPIView):
    """Класс представления вида Generic для эндпоинта изменения поставщика."""

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive]


class ProductsListAPIView(generics.ListAPIView):
    """Класс представления вида Generic для эндпоинта списка звеньев продаж."""

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    pagination_class = ProductsPaginator
    permission_classes = [IsAuthenticated, IsUserActive]


class ProductViewingAPIView(generics.RetrieveAPIView):
    """Класс представления вида Generic для эндпоинта просмотра привычки."""

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive]


class ProductDestroyAPIView(generics.DestroyAPIView):
    """Класс представления вида Generic для эндпоинта удаления привычки."""

    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated, IsUserActive, IsAdminUser]
