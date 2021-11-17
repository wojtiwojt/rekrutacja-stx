from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_of_books_view, name="book-list"),
    path("search/", views.list_of_books_view, name="search-book"),
    path("add-book/", views.add_or_edit_book_view, name="add-book"),
    path("edit-book/<int:pk>", views.add_or_edit_book_view, name="edit-book"),
]
