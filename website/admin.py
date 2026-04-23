from django.contrib import admin
from .models import (
    ContactMessage,
    Category,
    Product,
    ProductImage,
    Order,
    PayoutRequest,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'service_interest', 'created_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price_usd', 'price_sle', 'available', 'created_at')
    list_filter = ('available', 'category', 'created_at')
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name',
        'product',
        'quantity',
        'currency',
        'total_amount',
        'payment_status',
        'created_at',
    )
    list_filter = ('currency', 'payment_status', 'created_at')


@admin.register(PayoutRequest)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('seller', 'amount', 'status', 'request_date')
    list_filter = ('status', 'request_date')