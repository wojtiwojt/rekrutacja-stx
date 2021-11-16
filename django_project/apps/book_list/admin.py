from django.contrib import admin
from .models import Author, Book, IndustryIdentifiers

admin.site.register([Author, Book, IndustryIdentifiers])
