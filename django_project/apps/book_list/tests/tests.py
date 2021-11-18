from django import urls
from apps.book_list.forms import BookAddEditForm
from apps.book_list.models import Author, Book, IndustryIdentifiers
from apps.book_list.utils import (
    check_if_authors_exist_or_create_and_return_ids,
    get_existing_book_data_for_form,
    perform_search_on_given_parameters,
)
import pytest


def test_form_with_no_data():
    form = BookAddEditForm()
    assert not form.is_valid()


def test_form_validation_with_all_valid_data(full_book_form_valid_data):
    form = BookAddEditForm(full_book_form_valid_data)
    assert form.is_valid()


def test_form_validation_with_invalid_data(full_book_form_invalid_data):
    form = BookAddEditForm(full_book_form_invalid_data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_create_authors_from_string_when_no_authors(authors_string):
    assert Author.objects.all().count() == 0
    check_if_authors_exist_or_create_and_return_ids(authors_string)
    assert Author.objects.all().count() == 2


@pytest.mark.django_db
def test_create_authors_from_string_when_authors_in_db(authors_string, create_authors):
    assert Author.objects.all().count() == 2
    check_if_authors_exist_or_create_and_return_ids(authors_string)
    assert Author.objects.all().count() == 2


@pytest.mark.django_db
def test_get_data_from_model_for_form_on_edit(
    test_book_creation_view_with_valid_data, full_book_form_valid_data
):
    assert Book.objects.all().count() == 1
    assert Author.objects.all().count() == 2
    assert IndustryIdentifiers.objects.all().count() == 3
    book = Book.objects.all()[0]
    assert get_existing_book_data_for_form(book) == full_book_form_valid_data


@pytest.mark.django_db
def test_edit_view_on_existing_book(client, test_book_creation_view_with_valid_data):
    assert Book.objects.all().count() == 1
    book = Book.objects.all()[0]
    book_title = book.title
    data_from_model = get_existing_book_data_for_form(book)
    data_from_model["title"] = "Hobbit Boso Przez Świat"
    edit_book_url = urls.reverse("edit-book", kwargs={"pk": book.id})
    response = client.post(edit_book_url, data_from_model)
    assert response.status_code == 302
    book = Book.objects.all()[0]
    assert book_title != book.title


@pytest.mark.django_db
def test_book_creation_view_with_invalid_data(client, full_book_form_invalid_data):
    assert Book.objects.all().count() == 0
    add_book_url = urls.reverse("add-book")
    response = client.post(add_book_url, full_book_form_invalid_data)
    assert response.status_code == 200
    assert Book.objects.all().count() == 0


@pytest.mark.django_db
def test_search_function(create_three_books_for_search_or_delete):
    assert Book.objects.all().count() == 3
    assert Author.objects.all().count() == 2
    search_in_author = perform_search_on_given_parameters(
        title=None, author="Tolkien", language=None, date_start=None, date_end=None
    )
    assert len(search_in_author) == 2
    search_in_title = perform_search_on_given_parameters(
        title="Hobbit", author=None, language=None, date_start=None, date_end=None
    )
    assert len(search_in_title) == 2
    search_in_language = perform_search_on_given_parameters(
        title=None, author=None, language="polski", date_start=None, date_end=None
    )
    assert len(search_in_language) == 2
    search_in_date_from = perform_search_on_given_parameters(
        title=None, author=None, language=None, date_start="1990-1-1", date_end=None
    )
    assert len(search_in_date_from) == 1
    search_in_date_to = perform_search_on_given_parameters(
        title=None, author=None, language=None, date_start=None, date_end="1990-1-1"
    )
    assert len(search_in_date_to) == 2
    search_in_between = perform_search_on_given_parameters(
        title=None,
        author=None,
        language=None,
        date_start="1940-1-1",
        date_end="1990-1-1",
    )
    assert len(search_in_between) == 2
    # two models with same year, first one has only year, second has full date
    search_in_between = perform_search_on_given_parameters(
        title=None,
        author=None,
        language=None,
        date_start="1958-3-1",
        date_end="1990-1-1",
    )
    assert len(search_in_between) == 2
    # same situation as above, but date start is greater than date of model with full year
    search_in_between = perform_search_on_given_parameters(
        title=None,
        author=None,
        language=None,
        date_start="1958-7-1",
        date_end="1990-1-1",
    )
    assert len(search_in_between) == 1
    fail_search = perform_search_on_given_parameters(
        title=None,
        author="Żulczyk",
        language=None,
        date_start="1958-7-1",
        date_end="1990-1-1",
    )
    assert len(fail_search) == 0


@pytest.mark.django_db
def test_delete_single_book(client, create_three_books_for_search_or_delete):
    assert Book.objects.all().count() == 3
    book = Book.objects.all()[0]
    delete_single_book = urls.reverse("delete-book", kwargs={"pk": book.id})
    response = client.get(delete_single_book)
    assert response.status_code == 302
    assert Book.objects.all().count() == 2


@pytest.mark.django_db
def test_delete_all_books(client, create_three_books_for_search_or_delete):
    assert Book.objects.all().count() == 3
    delete_all_books = urls.reverse("delete-all")
    response = client.get(delete_all_books)
    assert response.status_code == 302
    assert Book.objects.all().count() == 0


@pytest.mark.django_db
def test_import_book_view(client):
    assert Book.objects.all().count() == 0
    assert Author.objects.all().count() == 0
    assert IndustryIdentifiers.objects.all().count() == 0
    import_url = urls.reverse("import-books")
    response = client.get(import_url, {"intitle": "Hobbit", "inauthor": "Tolkien"})
    assert response.status_code == 302
    assert Book.objects.all().count() > 0
    assert Author.objects.all().count() > 0
    assert IndustryIdentifiers.objects.all().count() > 0


@pytest.mark.django_db
def test_api_view(
    client, use_dummy_cache_backend, create_three_books_for_search_or_delete
):
    assert Book.objects.all().count() == 3
    api_url = urls.reverse("books-list-api")
    response = client.get(api_url)
    assert response.json()["total_items"] == 3
    api_url_with_params = urls.reverse("books-list-api")
    response = client.get(api_url_with_params, {"author": "Tolkien"})
    assert response.json()["total_items"] == 2
