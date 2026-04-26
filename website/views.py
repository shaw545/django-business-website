from django.shortcuts import render, get_object_or_404
from .models import Product, Category, ProductImage


def home(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    return render(request, "home.html", {
        "products": products,
        "categories": categories,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # ✅ GET ALL EXTRA IMAGES
    gallery_images = ProductImage.objects.filter(product=product)

    return render(request, "product_detail.html", {
        "product": product,
        "gallery_images": gallery_images,
    })