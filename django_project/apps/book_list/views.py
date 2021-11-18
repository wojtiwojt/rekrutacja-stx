from django.shortcuts import render, get_object_or_404, redirect
from urllib.request import urlopen
from urllib.parse import quote
from django.contrib import messages
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator
import json
from .forms import BookAddEditForm
from .models import Book, IndustryIdentifiers, Author
from .utils import (
    check_if_authors_exist_or_create_and_return_ids,
    get_existing_book_data_for_form,
    perform_search_on_given_parameters,
)


def add_or_edit_book_view(request, pk=None):
    if request.method == "POST":
        form = BookAddEditForm(request.POST)
        if pk:
            book = get_object_or_404(Book, id=pk)
        else:
            book = Book()
        if form.is_valid():
            book.title = form.cleaned_data["title"]
            book.publication_date_year = form.cleaned_data["publication_date_year"]
            book.publication_date_month = form.cleaned_data["publication_date_month"]
            book.publication_date_day = form.cleaned_data["publication_date_day"]
            book.page_count = form.cleaned_data["page_count"]
            book.cover_url = form.cleaned_data["cover_url"]
            book.publication_language = form.cleaned_data["publication_language"]
            book.save()
            book.authors.clear()
            list_of_authors = check_if_authors_exist_or_create_and_return_ids(
                form.cleaned_data["authors"]
            )
            book.authors.add(*list_of_authors)

            for id_type in ["isbn_10", "isbn_13", "other_id"]:
                try:
                    identifier_obj = book.identifier.get(id_type=id_type)
                    if form.cleaned_data[id_type]:
                        identifier_obj.identifier = form.cleaned_data[id_type]
                        identifier_obj.save()
                    else:
                        identifier_obj.delete()
                except:
                    if form.cleaned_data[id_type]:
                        IndustryIdentifiers.objects.create(
                            id_type=id_type,
                            identifier=form.cleaned_data[id_type],
                            book=book,
                        )
            messages.success(
                request, f'Pomyślnie zapisano tytuł "{form.cleaned_data["title"]}".'
            )
            return redirect("/")
        return render(request, "add_edit_form.html", {"form": form, "book": book})

    if pk:
        book = get_object_or_404(Book, id=pk)
        form = BookAddEditForm(get_existing_book_data_for_form(book))
    else:
        book = None
        form = BookAddEditForm()
    return render(request, "add_edit_form.html", {"form": form, "book": book})


def list_of_books_view(request):
    all_books_count = Book.objects.all().count()
    if request.GET:
        title = request.GET.get("title")
        author = request.GET.get("author")
        language = request.GET.get("language")
        date_start = request.GET.get("date_start")
        date_end = request.GET.get("date_end")
        if title or author or language or date_start or date_end:
            books = perform_search_on_given_parameters(
                title, author, language, date_start, date_end
            )
            messages.success(
                request, f"Liczba wyszukań dla wybranych kryteriów: {len(books)}"
            )
            paginator = Paginator(books, 5)
            page_number = request.GET.get("page")
            page_obj = paginator.get_page(page_number)
            return render(
                request,
                "book_list.html",
                {
                    "page_obj": page_obj,
                    "books_count": all_books_count,
                    "books_in_search": len(books),
                },
            )

    books = Book.objects.all().order_by("title")
    paginator = Paginator(books, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "book_list.html",
        {"page_obj": page_obj, "books_count": all_books_count},
    )


def import_books_from_api_view(request):
    if request.GET:
        base_url = "https://www.googleapis.com/books/v1/volumes?q="
        for param in request.GET:
            if param and request.GET[param]:
                base_url = base_url + f"+{param}:{quote(request.GET[param])}"

        url = base_url + "&projection=full&maxResults=40&printType=books"

        try:
            response = urlopen(url)
        except:
            messages.warning(request, f"Wypełnij chociaż jedno z pól")
            return render(request, "import.html")

        data_json = json.loads(response.read().decode())

        index = 0
        url_list = []
        url_list.append(url + f"&startIndex={0}")
        while index < data_json["totalItems"] and data_json["totalItems"] - index > 40:
            index += 40
            url_list.append(url + f"&startIndex={index}")

        languages_file = open(finders.find("books/lang_codes.json"), "r")
        languages_json = json.loads(languages_file.read())

        books_imported_count = 0
        for url in url_list:
            response = urlopen(url)
            data_json = json.loads(response.read().decode())
            messages.info(request, f"Zapytanie do API google books: {url}")
            if data_json["totalItems"] > 0:
                for item in data_json["items"]:
                    book = Book()
                    authors = []
                    industry_identifiers = []
                    errors = []
                    existing_identifiers_in_db = []
                    for volume_info in item["volumeInfo"]:
                        if volume_info == "title":
                            book.title = item["volumeInfo"][volume_info]
                        if volume_info == "authors":
                            for author in item["volumeInfo"][volume_info]:
                                authors.append(author)
                        if volume_info == "publishedDate":
                            string_date = item["volumeInfo"][volume_info].split("-")
                            try:
                                book.publication_date_year = int(string_date[0])
                            except IndexError:
                                pass
                            except:
                                errors.append(f"Błędny format roku {string_date}")
                            try:
                                book.publication_date_month = int(string_date[1])
                            except IndexError:
                                pass
                            except:
                                errors.append("Błędny format miesiąca")
                            try:
                                book.publication_date_day = int(string_date[2])
                            except IndexError:
                                pass
                            except:
                                errors.append("Błędny format dnia")
                        if volume_info == "pageCount":
                            book.page_count = item["volumeInfo"][volume_info]
                        if volume_info == "industryIdentifiers":
                            for identifier in item["volumeInfo"][volume_info]:
                                if IndustryIdentifiers.objects.filter(
                                    identifier=identifier["identifier"]
                                ).exists():
                                    identifier_type = identifier["type"]
                                    identifier_id = identifier["identifier"]
                                    existing_identifiers_in_db.append(
                                        f"{identifier_type} - {identifier_id}"
                                    )
                                if identifier["type"] == "ISBN_10":
                                    industry_identifiers.append(
                                        {
                                            "id_type": "isbn_10",
                                            "identifier": identifier["identifier"],
                                        }
                                    )
                                if identifier["type"] == "ISBN_13":
                                    industry_identifiers.append(
                                        {
                                            "id_type": "isbn_13",
                                            "identifier": identifier["identifier"],
                                        }
                                    )
                                if identifier["type"] == "OTHER":
                                    industry_identifiers.append(
                                        {
                                            "id_type": "other_id",
                                            "identifier": identifier["identifier"],
                                        }
                                    )
                        if volume_info == "imageLinks":
                            if item["volumeInfo"][volume_info]["smallThumbnail"]:
                                book.cover_url = item["volumeInfo"][volume_info][
                                    "smallThumbnail"
                                ]
                        if volume_info == "language":
                            for language in languages_json:
                                if (
                                    item["volumeInfo"][volume_info].lower()
                                    == language["value"]
                                ):
                                    book.publication_language = language["text"]

                    if not existing_identifiers_in_db:
                        book.save()
                        books_imported_count += 1
                        if not authors:
                            errors.append("W api google pole z autorami było puste.")
                        if errors:
                            errors.append(
                                f"id książki z błedami: {book.id}, "
                                f'Tytuł "{book.title}" Pomimo to, tytuł został dodany.'
                            )
                            error_message = " / ".join(errors)
                            messages.warning(request, error_message)
                        for author in authors:
                            if Author.objects.filter(name=author).exists():
                                existing_author = Author.objects.get(name=author)
                                book.authors.add(existing_author)
                            else:
                                new_author = Author.objects.create(name=author)
                                book.authors.add(new_author)

                        for identifier in industry_identifiers:
                            IndustryIdentifiers.objects.create(**identifier, book=book)
                    else:
                        messages.warning(
                            request,
                            f'Nie zaimportowano ksiązki "{book.title}" z '
                            f"powodu instenijących w bazie numerów isbn: {existing_identifiers_in_db}. "
                            f"Prawdopodobnie ten tytuł znajduje się w bazie.",
                        )
            else:
                messages.warning(
                    request, f"Nie znaleziono wyników dla wybranych słów kluczowych."
                )
        messages.success(
            request, f"Liczba zaimportowanych książek: {books_imported_count}"
        )
        return redirect("/")
    return render(request, "import.html")


def detele_book_view(request, pk):
    book = get_object_or_404(Book, id=pk)
    messages.success(request, f'Poprawnie usunięto tytuł "{book.title}"')
    book.delete()
    return redirect("/")


def delete_all_books(request):
    Book.objects.all().delete()
    messages.success(request, "Usunięto wszystkie książki.")
    return redirect("/")
