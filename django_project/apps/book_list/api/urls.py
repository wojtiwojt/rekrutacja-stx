from django.urls import path
from . import views


urlpatterns = [
    path("books/", views.BookListAPIView.as_view(), name="books-list-api"),
]
