from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
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


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    cart[product_id] = cart.get(product_id, 0) + 1
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
        product.quantity = quantity
        product.subtotal = product.amount * quantity
        total += product.subtotal
        products.append(product)

    return render(request, "cart.html", {"products": products, "total": total})


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

    return render(request, "checkout.html", {"products": products, "total": total})


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email") or ""
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        return redirect("login")

    return render(request, "register.html")


def seller_dashboard(request):
    products = Product.objects.all()
    total_products = products.count()
    total_value = sum(product.amount for product in products)

    return render(request, "dashboard.html", {
        "products": products,
        "total_products": total_products,
        "total_value": total_value,
    })


def add_product(request):
    if request.method == "POST":
        Product.objects.create(
            name=request.POST.get("name"),
            category=request.POST.get("category"),
            amount=request.POST.get("amount"),
            description=request.POST.get("description"),
            condition=request.POST.get("condition"),
            image=request.FILES.get("image"),
        )
        return redirect("seller_dashboard")

    return render(request, "product_form.html")


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.category = request.POST.get("category")
        product.amount = request.POST.get("amount")
        product.description = request.POST.get("description")
        product.condition = request.POST.get("condition")

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()
        return redirect("dashboard")

    return render(request, "product_form.html", {"product": product})s

def terms_view(request):
    return render(request, "terms.html")


def privacy_view(request):
    return render(request, "privacy.html")