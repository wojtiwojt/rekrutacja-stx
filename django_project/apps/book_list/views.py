from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from datetime import date
from .forms import BookAddEditForm
from .models import Book, IndustryIdentifiers
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
    if request.GET:
        title = request.GET.get('title')
        author = request.GET.get('author')
        language = request.GET.get('language')
        date_start = request.GET.get('date_start')
        date_end = request.GET.get('date_end')

        print(request.GET)

        filters = {}
        if title:
            filters['title__icontains'] = title
        if author:
            filters['authors__name__icontains'] = author
        if language:
            filters['publication_language__icontains'] = language
        if date_start:
            date_list = date_start.split('-')
            date_from_query = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
            filters['publication_date_year__gte'] = date_from_query.year 
        if date_end:
            date_list = date_end.split('-')
            date_end_query = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
            filters['publication_date_year__lte'] = date_end_query.year
    
        books = Book.objects.filter(**filters).distinct()

        books_filtered = []
        for i in books:
            if not i.publication_date_month and not i.publication_date_day:
                books_filtered.append(i)
            if i.publication_date_month and i.publication_date_day:
                if date_from_query <= date(i.publication_date_year, i.publication_date_month, i.publication_date_day) <= date_end_query:
                    books_filtered.append(i)
            if i.publication_date_month and not i.publication_date_day:
                if date_from_query <= date(i.publication_date_year, i.publication_date_month, 1) <= date_end_query:
                    books_filtered.append(i)

        return render(request, "book_list.html", {'books': books_filtered})
    
    books = Book.objects.all()
    return render(request, "book_list.html", {'books': books})