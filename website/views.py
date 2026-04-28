from django.shortcuts import render, get_object_or_404, redirect
from .models import Product


def get_product_value(product):
    if hasattr(product, "amount") and product.amount is not None:
        return product.amount

    if hasattr(product, "price") and product.price is not None:
        return product.price

    return 0


def home(request):
    products = Product.objects.all()

    for product in products:
        product.display_price = get_product_value(product)

    return render(request, "home.html", {"products": products})


def products_view(request):
    products = Product.objects.all()

    for product in products:
        product.display_price = get_product_value(product)

    return render(request, "products.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.display_price = get_product_value(product)

    return render(request, "product_detail.html", {"product": product})


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


def buy_now(request, product_id):
    request.session["cart"] = {str(product_id): 1}
    request.session.modified = True

    return redirect("checkout")


def cart_view(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        value = get_product_value(product)

        product.quantity = quantity
        product.display_price = value
        product.subtotal = value * quantity

        total += product.subtotal
        products.append(product)

    return render(request, "cart.html", {
        "products": products,
        "total": total,
    })


def checkout_view(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        value = get_product_value(product)

        product.quantity = quantity
        product.display_price = value
        product.subtotal = value * quantity

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