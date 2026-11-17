from django.contrib import admin
from .models import Category, Product, Review, Cart, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "user", "category", "quantity", "price"]
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "user", "rating"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total", "is_paid", "created_at"]
    list_filter = ["is_paid"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "client", "product", "quantity", "price"]

    def client(self, obj):
        return obj.order.user
    client.short_description = "Клиент"


admin.site.register(Cart)
