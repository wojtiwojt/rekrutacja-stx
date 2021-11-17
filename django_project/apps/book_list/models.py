from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, blank=False)
    authors = models.ManyToManyField(Author)
    publication_date_year = models.PositiveSmallIntegerField(null=True, blank=True)
    publication_date_month = models.PositiveSmallIntegerField(null=True, blank=True)
    publication_date_day = models.PositiveSmallIntegerField(null=True, blank=True)
    publication_date_string = models.CharField(max_length=255, null=True, blank=True)
    page_count = models.PositiveSmallIntegerField(null=True, blank=True)
    cover_url = models.URLField(max_length=255, null=True, blank=True)
    publication_language = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return f'{self.title} - {self.publication_date_year} / {self.publication_date_month} / {self.publication_date_day}'

    def save(self, *args, **kwargs):
        all_spare_dates = []
        if self.publication_date_year:
            all_spare_dates.append(str(self.publication_date_year))
        if self.publication_date_month:
            all_spare_dates.append(str(self.publication_date_month))
        if self.publication_date_day:
            all_spare_dates.append(str(self.publication_date_day))
        self.publication_date_string = '-'.join(all_spare_dates)
        super(Book, self).save(*args, **kwargs)



class IndustryIdentifiers(models.Model):
    id_type = models.CharField(max_length=255, blank=False)
    identifier = models.CharField(max_length=255, blank=False)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="identifier", blank=False
    )

    def __str__(self):
        return f"{self.id_type}-{self.identifier} / {self.book.title}"
