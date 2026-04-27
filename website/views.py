from django.shortcuts import render, get_object_or_404, redirect
from .models import Product


# ======================
# HOME / PRODUCTS
# ======================
def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})


def products_view(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})


# ======================
# PRODUCT DETAIL
# ======================
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


# ======================
# CART & BUY
# ======================
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", [])
    cart.append(product.id)
    request.session["cart"] = cart

    return redirect("cart")


def buy_now(request, product_id):
    return redirect("checkout")


def cart_view(request):
    cart = request.session.get("cart", [])
    products = Product.objects.filter(id__in=cart)
    return render(request, "cart.html", {"products": products})


def checkout_view(request):
    return render(request, "checkout.html")


# ======================
# STATIC PAGES
# ======================
def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html")


def contact(request):
    return render(request, "contact.html")


def terms_view(request):
    return render(request, "terms.html")


def privacy_view(request):
    return render(request, "privacy.html")


def portfolio(request):
    return render(request, "portfolio.html")


def login_view(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


# OPTIONAL (fix dashboard error)
def seller_dashboard(request):
    return render(request, "dashboard.html")