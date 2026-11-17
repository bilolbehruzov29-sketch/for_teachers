from django.db import connection
from django.test.utils import CaptureQueriesContext
from books.models import Book, Review, Author


with CaptureQueriesContext(connection) as q1:
    for book in Book.objects.all():
        book.author.full_name
        list(book.categories.all())

with CaptureQueriesContext(connection) as q2:
    for book in Book.objects.select_related("author").prefetch_related("categories"):
        book.author.full_name
        list(book.categories.all())

print("Книги:", len(q1), "->", len(q2))


with CaptureQueriesContext(connection) as q1:
    for review in Review.objects.all():
        review.book.author.full_name

with CaptureQueriesContext(connection) as q2:
    for review in Review.objects.select_related("book", "book__author"):
        review.book.author.full_name

print("Отзывы:", len(q1), "->", len(q2))


with CaptureQueriesContext(connection) as q1:
    for author in Author.objects.all():
        for book in author.books.all():
            list(book.categories.all())

with CaptureQueriesContext(connection) as q2:
    for author in Author.objects.prefetch_related("books__categories"):
        for book in author.books.all():
            list(book.categories.all())

print("Авторы:", len(q1), "->", len(q2))
