from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookAddEditForm
from .models import Author, Book, IndustryIdentifiers
from .utils import (
    check_if_authors_exist_or_create_and_return_ids,
    get_existing_book_data_for_form,
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
                    identifier_obj.identifier = form.cleaned_data[id_type]
                    identifier_obj.save()
                except:
                    IndustryIdentifiers.objects.create(
                        id_type=id_type,
                        identifier=form.cleaned_data[id_type],
                        book=book,
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
