from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime


def validate_year(value):
    year = datetime.now().year
    if value not in range(1600, datetime.now().year + 2):
        raise ValidationError(
            _("Wybierz rok od 1600 do %(year)s."),
            params={"year": year},
        )


def validate_month(value):
    if value not in range(1, 13):
        raise ValidationError("Pamiętaj, że rok ma 12 miesięcy.")


def validate_isbn_if_numbers(value):
    try:
        int(value)
    except ValueError:
        raise ValidationError(
            "Identyfikator ISBN powinien składać się wyłącznie z cyfr."
        )


def validate_isbn_10_length(value):
    if len(value) != 10:
        raise ValidationError("Identyfikator ISBN-10 powinien mieć dokładnie 10 cyfr.")


def validate_isbn_13_length(value):
    if len(value) != 13:
        raise ValidationError("Identyfikator ISBN-13 powinien mieć dokładnie 13 cyfr.")
