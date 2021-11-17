from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from .serializers import BookSerializer
from .pagination import BookListPagination
from ..models import Book
from ..utils import perform_search_on_given_parameters


class BookListAPIView(generics.ListAPIView):
    serializer_class = BookSerializer
    pagination_class = BookListPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        if self.request.query_params:
            title = self.request.query_params.get("title")
            author = self.request.query_params.get("author")
            language = self.request.query_params.get("language")
            date_start = self.request.query_params.get("date_start")
            date_end = self.request.query_params.get("date_end")

            book_list = perform_search_on_given_parameters(
                title, author, language, date_start, date_end
            )
            return book_list

        return Book.objects.all().order_by("title")
