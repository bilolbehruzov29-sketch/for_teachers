from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.contrib.auth.models import User
from main.models import Product, Review


with CaptureQueriesContext(connection) as q1:
    for product in Product.objects.all():
        product.user.username
        product.category.name

with CaptureQueriesContext(connection) as q2:
    for product in Product.objects.select_related("user", "category"):
        product.user.username
        product.category.name

print("Продукты:", len(q1), "->", len(q2))


with CaptureQueriesContext(connection) as q1:
    for review in Review.objects.all():
        review.product.name
        review.user.username

with CaptureQueriesContext(connection) as q2:
    for review in Review.objects.select_related("product", "user"):
        review.product.name
        review.user.username

print("Отзывы:", len(q1), "->", len(q2))


with CaptureQueriesContext(connection) as q1:
    for user in User.objects.all():
        for product in user.products.all():
            product.category.name

with CaptureQueriesContext(connection) as q2:
    for user in User.objects.prefetch_related("products__category"):
        for product in user.products.all():
            product.category.name

print("Продавцы:", len(q1), "->", len(q2))
