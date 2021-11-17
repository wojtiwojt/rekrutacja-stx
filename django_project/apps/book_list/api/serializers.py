from rest_framework import serializers
from ..models import Book


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    publication_date = serializers.SerializerMethodField()
    industry_identifiers = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "title",
            "authors",
            "publication_date",
            "page_count",
            "cover_url",
            "publication_language",
            "industry_identifiers",
        ]

    def get_authors(self, instance):
        author_names = [author.name for author in instance.authors.all()]
        return author_names

    def get_publication_date(self, instance):
        return instance.publication_date_string

    def get_industry_identifiers(self, instance):
        identifiers = [
            {"type": i.id_type, "identifier": i.identifier}
            for i in instance.identifier.all()
        ]
        return identifiers
