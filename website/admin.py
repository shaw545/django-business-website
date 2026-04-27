from django.contrib import admin
from .models import Category, Product, ProductImage


# ======================
# INLINE FOR MULTIPLE IMAGES
# ======================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3   # number of empty image fields to show


# ======================
# PRODUCT ADMIN
# ======================
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
    search_fields = ("name",)
    list_filter = ("category",)

    # This allows adding multiple images inside product
    inlines = [ProductImageInline]


# ======================
# REGISTER MODELS
# ======================
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)