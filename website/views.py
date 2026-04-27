from django.shortcuts import render, get_object_or_404, redirect
from .models import Product


def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})


def products_view(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


# ✅ ADD TO CART
def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


# ✅ BUY NOW
def buy_now(request, product_id):
    request.session["cart"] = {str(product_id): 1}
    request.session.modified = True
    return redirect("checkout")


# ✅ CART PAGE
def cart_view(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        product.quantity = quantity
        product.subtotal = product.amount * quantity

        total += product.subtotal
        products.append(product)

    return render(request, "cart.html", {
        "products": products,
        "total": total,
    })


# ✅ CHECKOUT PAGE
def checkout_view(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        product.quantity = quantity
        product.subtotal = product.amount * quantity

        total += product.subtotal
        products.append(product)

    return render(request, "checkout.html", {
        "products": products,
        "total": total,
    })
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


def login_view(request):
    return render(request, "login.html")


def register(request):
    return render(request, "register.html")


def seller_dashboard(request):
    return render(request, "dashboard.html")