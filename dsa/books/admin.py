from django.contrib import admin
from .models import Author, Category, Book, Review, Cart, Order, OrderItem


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "price", "published_year", "in_stock"]
    search_fields = ["title"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total", "is_paid", "created_at"]
    list_filter = ["is_paid"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "client", "book", "quantity", "price"]

    def client(self, obj):
        return obj.order.user
    client.short_description = "Клиент"


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Cart)
