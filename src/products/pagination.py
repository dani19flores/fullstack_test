from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination

class ProductPagination(PageNumberPagination):
    #page_size = 10
    page_query_param = 'p' #page number query parameter
    page_size_query_param = 'size'
    max_page_size = 5
    last_page_strings = "end" #last page query parameter

class ProductLDPagionation(LimitOffsetPagination):
    default_limit = 5
    max_limit = 7
    limit_query_param = 'records'
    offset_query_param = 'start'

class ProductCPagination(CursorPagination):
    page_size = 4
    cursor_query_param = 'cur'
    ordering = 'created_at'