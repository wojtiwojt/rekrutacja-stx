import pytest
from django import urls
from apps.book_list.models import Author, Book, IndustryIdentifiers


@pytest.fixture
def authors_string():
    return "Kowalski, Mickieiwcz"


@pytest.fixture
def create_authors():
    Author.objects.create(name="Kowalski")
    Author.objects.create(name="Mickieiwcz")
    assert Author.objects.all().count() == 2


@pytest.fixture
def full_book_form_valid_data():
    data = {
        "title": "Hobbit",
        "authors": "Tolkien, Aragorn",
        "publication_date_year": 1958,
        "publication_date_month": 12,
        "publication_date_day": 1,
        "page_count": 253,
        "cover_url": "http://books.google.com/books/content?id=4kBGzgEACAAJ&printsec=frontcover&img=1&zoom=5&source=gbs_api",
        "publication_language": "język polski (pl)",
        "isbn_10": "1234567890",
        "isbn_13": "1234567890123",
        "other_id": "OSNSNN123",
    }
    return data


@pytest.fixture
def full_book_form_invalid_data():
    data = {
        "title": "Hobbit",
        "authors": "Tolkien, Aragorn",
        "publication_date_month": 12,
        "publication_date_day": 1,
        "page_count": 253,
        "cover_url": "http://books.google.com/books/content?id=4kBGzgEACAAJ&printsec=frontcover&img=1&zoom=5&source=gbs_api",
        "publication_language": "język polski (pl)",
    }
    return data


@pytest.fixture
@pytest.mark.django_db
def test_book_creation_view_with_valid_data(client, full_book_form_valid_data):
    assert Book.objects.all().count() == 0
    assert Author.objects.all().count() == 0
    assert IndustryIdentifiers.objects.all().count() == 0
    add_book_url = urls.reverse("add-book")
    response = client.post(add_book_url, full_book_form_valid_data)
    assert response.status_code == 302
    assert Book.objects.all().count() == 1
    assert Author.objects.all().count() == 2
    assert IndustryIdentifiers.objects.all().count() == 3


@pytest.fixture
@pytest.mark.django_db
def create_three_books_for_search_or_delete():
    assert Book.objects.all().count() == 0
    assert Author.objects.all().count() == 0

    book_one = Book.objects.create(
        title="Hobbit",
        publication_language="język polski (pl)",
        publication_date_year=1958,
        publication_date_month=5,
        publication_date_day=12,
    )
    book_two = Book.objects.create(
        title="Ślepnąc od świateł",
        publication_language="język polski (pl)",
        publication_date_year=2000,
        publication_date_month=1,
        publication_date_day=12,
    )
    book_three = Book.objects.create(
        title="Hobbit pierwsza część",
        publication_language="język angielski (en)",
        publication_date_year=1958,
    )
    author_one = Author.objects.create(name="Tolkien")
    author_two = Author.objects.create(name="Żulczyk")

    book_one.authors.add(author_one)
    book_two.authors.add(author_two)
    book_three.authors.add(author_one)

    assert Book.objects.all().count() == 3
    assert Author.objects.all().count() == 2


@pytest.fixture(autouse=True)
def use_dummy_cache_backend(settings):
    settings.REST_FRAMEWORK = {
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
    }
