from django.urls import path
from electronics_store.apps import ElectronicsStoreConfig
from electronics_store.views import (
    SupplierCreateAPIView, SuppliersListAPIView, SupplierViewingAPIView, SupplierUpdateAPIView,
    SupplierDestroyAPIView,
    ContactsListAPIView, ContactViewingAPIView, ContactCreateAPIView, ContactUpdateAPIView,
    ContactDestroyAPIView,
    ProductViewingAPIView, ProductsListAPIView, ProductCreateAPIView, ProductUpdateAPIView,
    ProductDestroyAPIView,
)


app_name = ElectronicsStoreConfig.name

urlpatterns = [
    path('suppliers/', SuppliersListAPIView.as_view(), name='suppliers'),
    path('supplier/<int:pk>/', SupplierViewingAPIView.as_view(), name='supplier'),
    path('supplier/new/', SupplierCreateAPIView.as_view(), name='adding_supplier'),
    path('supplier/<int:pk>/update/', SupplierUpdateAPIView.as_view(), name='update_supplier'),
    path('supplier/<int:pk>/delete/', SupplierDestroyAPIView.as_view(), name='delete_supplier'),
    path('contacts/', ContactsListAPIView.as_view(), name='contacts'),
    path('contact/<int:pk>/', ContactViewingAPIView.as_view(), name='contact'),
    path('contact/new/', ContactCreateAPIView.as_view(), name='adding_contact'),
    path('contact/<int:pk>/update/', ContactUpdateAPIView.as_view(), name='update_contact'),
    path('contact/<int:pk>/delete/', ContactDestroyAPIView.as_view(), name='delete_contact'),
    path('products/', ProductsListAPIView.as_view(), name='products'),
    path('product/<int:pk>/', ProductViewingAPIView.as_view(), name='product'),
    path('product/new/', ProductCreateAPIView.as_view(), name='adding_product'),
    path('product/<int:pk>/update/', ProductUpdateAPIView.as_view(), name='update_product'),
    path('product/<int:pk>/delete/', ProductDestroyAPIView.as_view(), name='delete_product'),
]
