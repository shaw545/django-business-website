from django.contrib import admin
from .models import ContactMessage, Product, Order

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'service_interest', 'created_at')
    search_fields = ('name', 'email', 'company', 'message')
    list_filter = ('service_interest', 'created_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price_usd', 'price_sle', 'available', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('available', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'product', 'quantity', 'currency', 'total_amount', 'created_at')
    search_fields = ('customer_name', 'email', 'phone', 'address')
    list_filter = ('currency', 'created_at')