from django.contrib import admin
from .models import Product, Order, OrderItem, SellerProfile, ProductColor
from .models import ProductImage
from .models import SupportTicket

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(SellerProfile)
admin.site.register(ProductImage)
admin.site.register(ProductColor)
admin.site.register(SupportTicket)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "discount_price", "is_deal", "deal_label")
    list_filter = ("is_deal", "category")
    search_fields = ("name",)