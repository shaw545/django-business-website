from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    Order,
    ContactMessage,
    PayoutRequest,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "seller",
        "category",
        "price_usd",
        "price_sle",
        "available",
        "created_at",
    )
    list_filter = ("available", "category", "created_at")
    search_fields = ("name", "description")
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "created_at")
    search_fields = ("product__name",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "product",
        "quantity",
        "currency",
        "total_amount",
        "payment_status",
        "created_at",
    )
    list_filter = ("currency", "payment_status", "created_at")
    search_fields = ("customer_name", "email", "phone", "product__name")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "company",
        "service_interest",
        "created_at",
    )
    search_fields = ("name", "email", "company", "service_interest")


@admin.register(PayoutRequest)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "seller",
        "amount",
        "status",
        "request_date",
    )
    list_filter = ("status", "request_date")
    search_fields = ("seller__username",)