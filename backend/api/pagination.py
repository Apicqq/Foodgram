from rest_framework.pagination import PageNumberPagination


class PageNumberPaginator(PageNumberPagination):
    page_size_query_param = 'limit'
