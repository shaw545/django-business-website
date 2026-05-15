from django.contrib import admin
from .models import Product, Order, OrderItem, SellerProfile

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(SellerProfile)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "discount_price", "is_deal", "deal_label")
    list_filter = ("is_deal", "category")
    search_fields = ("name",)