# Generated by Django 3.2.9 on 2021-11-15 20:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "publication_date_year",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "publication_date_month",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "publication_date_day",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                ("page_count", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("cover_url", models.URLField(blank=True, max_length=255, null=True)),
                ("publication_language", models.CharField(max_length=255)),
                ("authors", models.ManyToManyField(to="book_list.Author")),
            ],
        ),
        migrations.CreateModel(
            name="IndustryIdentifiers",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("id_type", models.CharField(max_length=255)),
                ("identifier", models.CharField(max_length=255)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="book",
                        to="book_list.book",
                    ),
                ),
            ],
        ),
    ]
