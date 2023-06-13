from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """Пагинатор для определения количества элементов на странице."""
    page_size = 6
    # page_size_query_param = 'page_size'
    page_size_query_param = 'limit'
    max_page_size = 15
