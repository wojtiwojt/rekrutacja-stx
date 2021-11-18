from datetime import date
from .models import Author, Book


def check_if_authors_exist_or_create_and_return_ids(authors_string):
    separate_authors_names = authors_string.split(",")
    authors_list = []
    for author in separate_authors_names:
        if Author.objects.filter(name=author.strip()).exists():
            author = Author.objects.get(name=author.strip())
            authors_list.append(author)
        else:
            author = Author.objects.create(name=author.strip())
            authors_list.append(author)
    return authors_list


def get_existing_book_data_for_form(book):
    authors_list = [author.name for author in book.authors.all()]
    authors_one_string = ", ".join(authors_list)

    data = {
        "title": book.title,
        "authors": authors_one_string,
        "publication_date_year": book.publication_date_year,
        "publication_date_month": book.publication_date_month,
        "publication_date_day": book.publication_date_day,
        "page_count": book.page_count,
        "cover_url": book.cover_url,
        "publication_language": book.publication_language,
    }

    for industry_identifier in book.identifier.all():
        data[industry_identifier.id_type] = industry_identifier.identifier

    return data


def perform_search_on_given_parameters(title, author, language, date_start, date_end):
    filters = {}
    date_from_query = None
    date_end_query = None
    if title:
        filters["title__icontains"] = title
    if author:
        filters["authors__name__icontains"] = author
    if language:
        filters["publication_language__icontains"] = language
    if date_start:
        date_list = date_start.split("-")
        date_from_query = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
        filters["publication_date_year__gte"] = date_from_query.year
    if date_end:
        date_list = date_end.split("-")
        date_end_query = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
        filters["publication_date_year__lte"] = date_end_query.year

    books = Book.objects.filter(**filters).distinct().order_by("title")

    if date_from_query or date_end_query:
        books_filtered = []
        for book in books:
            if not book.publication_date_month and not book.publication_date_day:
                books_filtered.append(book)
            if not date_end_query:
                if book.publication_date_month and book.publication_date_day:
                    if date_from_query <= date(
                        book.publication_date_year,
                        book.publication_date_month,
                        book.publication_date_day,
                    ):
                        books_filtered.append(book)
                if book.publication_date_month and not book.publication_date_day:
                    if date_from_query <= date(
                        book.publication_date_year, book.publication_date_month, 1
                    ):
                        books_filtered.append(book)
            if not date_from_query:
                if book.publication_date_month and book.publication_date_day:
                    if (
                        date(
                            book.publication_date_year,
                            book.publication_date_month,
                            book.publication_date_day,
                        )
                        <= date_end_query
                    ):
                        books_filtered.append(book)
                if book.publication_date_month and not book.publication_date_day:
                    if (
                        date(book.publication_date_year, book.publication_date_month, 1)
                        <= date_end_query
                    ):
                        books_filtered.append(book)
            if date_from_query and date_end_query:
                if book.publication_date_month and book.publication_date_day:
                    if (
                        date_from_query
                        <= date(
                            book.publication_date_year,
                            book.publication_date_month,
                            book.publication_date_day,
                        )
                        <= date_end_query
                    ):
                        books_filtered.append(book)
                if book.publication_date_month and not book.publication_date_day:
                    if (
                        date_from_query
                        <= date(
                            book.publication_date_year, book.publication_date_month, 1
                        )
                        <= date_end_query
                    ):
                        books_filtered.append(book)
        return books_filtered
    return books
