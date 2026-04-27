from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category


def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "home.html", {
        "products": products,
        "categories": categories,
    })


def products(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, "products.html", {
        "products": products,
        "categories": categories,
    })


def product_list(request):
    return products(request)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {
        "product": product,
    })


def add_to_cart(request, product_id):
    get_object_or_404(Product, id=product_id)
    return redirect("cart")


def buy_now(request, product_id):
    get_object_or_404(Product, id=product_id)
    return redirect("checkout")


def cart(request):
    return render(request, "cart.html")


def cart_checkout(request):
    return render(request, "cart_checkout.html")


def checkout(request):
    return render(request, "checkout.html")


def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html")


def contact(request):
    return render(request, "contact.html")


def privacy(request):
    return render(request, "privacy.html")


def portfolio(request):
    return render(request, "portfolio.html")


def login_view(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def add_product(request):
    return render(request, "add_product.html")


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "edit_product.html", {
        "product": product,
    })


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect("products")

    return render(request, "delete_product.html", {
        "product": product,
    })