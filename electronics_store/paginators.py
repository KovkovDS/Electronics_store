from rest_framework.pagination import PageNumberPagination


class SuppliersPaginator(PageNumberPagination):
    """ Класс пагинации для эндпоинта списка звеньев сети продаж."""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 10
