from .models import Author


def check_if_authors_exist_or_create_and_return_ids(authors_string):
    separate_authors_names = authors_string.split(",")
    authors_list = []
    for author in separate_authors_names:
        try:
            author = Author.objects.get(name=author.strip())
            authors_list.append(author)
        except:
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
