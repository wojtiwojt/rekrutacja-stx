from django import forms
from datetime import date
from .validators import (
    validate_year,
    validate_month,
    validate_isbn_10_length,
    validate_isbn_13_length,
    validate_isbn_if_numbers,
)
from .lang_choices import LANGUAGE_CHOICES


class BookAddEditForm(forms.Form):
    title = forms.CharField(max_length=255, label="Tytuł")
    authors = forms.CharField(
        max_length=255,
        label="Autor lub autorzy",
        help_text="W przypadku większej liczby autorów wpisz ich po przecinku, np. Adam Mickiewicz, Julian Tuwim",
    )
    publication_date_year = forms.IntegerField(
        required=False, validators=[validate_year], label="Rok wydania"
    )
    publication_date_month = forms.IntegerField(
        required=False, validators=[validate_month], label="Miesiąc wydania"
    )
    publication_date_day = forms.IntegerField(required=False, label="Dzień wydania")
    page_count = forms.IntegerField(label="Liczba stron")
    cover_url = forms.URLField(
        max_length=255,
        label="Link do okładki",
        required=False,
    )
    publication_language = forms.ChoiceField(
        label="Język publikacji",
        required=False,
        choices=LANGUAGE_CHOICES,
        help_text="Zacznij pisać i wybierz język z listy",
    )
    isbn_10 = forms.CharField(
        max_length=255,
        label="ISBN-10",
        required=False,
        validators=[validate_isbn_10_length, validate_isbn_if_numbers],
    )
    isbn_13 = forms.CharField(
        max_length=255,
        label="ISBN-13",
        required=False,
        validators=[validate_isbn_13_length, validate_isbn_if_numbers],
    )
    other_id = forms.CharField(
        max_length=255, label="Inny rodzaj oznaczenia", required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        publication_date_year = cleaned_data.get("publication_date_year")
        publication_date_month = cleaned_data.get("publication_date_month")
        publication_date_day = cleaned_data.get("publication_date_day")
        isbn_10 = cleaned_data.get("isbn_10")
        isbn_13 = cleaned_data.get("isbn_13")
        other_id = cleaned_data.get("other_id")

        if publication_date_year and publication_date_month and publication_date_day:
            try:
                date(
                    publication_date_year, publication_date_month, publication_date_day
                )
            except ValueError:
                msg = "Sprawdź poprawność"
                self.add_error("publication_date_year", msg)
                self.add_error("publication_date_month", msg)
                self.add_error("publication_date_day", msg)
                raise forms.ValidationError("Wpisana została niepoprawna data")
        elif not publication_date_year:
            self.add_error(
                "publication_date_year", "Musisz podać chociaż rok publikacji"
            )
        elif (
            publication_date_year
            and not publication_date_month
            and publication_date_day
        ):
            self.add_error("publication_date_month", "Musisz podać jeszcze miesiąc")

        if not isbn_10 and not isbn_13 and not other_id:
            msg = "Przynajmniej jedno z pól numeru identyfikacji musi zostać wypełnione"
            self.add_error("isbn_10", msg)
            self.add_error("isbn_13", msg)
            self.add_error("other_id", msg)
        return cleaned_data
