from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Product
from .models import Product, Order, OrderItem


# =========================
# PUBLIC VIEWS
# =========================

def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})


def products_view(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


# =========================
# CART
# =========================

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


# =========================
# CHECKOUT
# =========================

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

    if request.method == "POST":
        # Create Order
        order = Order.objects.create(
            buyer_name=request.POST.get("buyer_name"),
            buyer_phone=request.POST.get("buyer_phone"),
            buyer_email=request.POST.get("buyer_email"),
            buyer_address=request.POST.get("buyer_address"),
            payment_method=request.POST.get("payment_method"),
            total_amount=total,
        )

        # Create Order Items (VERY IMPORTANT for seller dashboard)
        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,   # 🔥 THIS is what links seller to order
                quantity=product.quantity,
                price=product.amount,
            )

        # Clear cart
        request.session["cart"] = {}
        request.session["last_order_id"] = order.id
        request.session.modified = True

        return redirect("order_confirmation")

    return render(request, "checkout.html", {
        "products": products,
        "total": total,
    })

def order_confirmation(request):
    return render(request, "order_confirmation.html")


# =========================
# AUTH
# =========================

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        return redirect("login")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("home")


# =========================
# SELLER DASHBOARD
# =========================

@login_required
def seller_dashboard(request):
    products = Product.objects.filter(seller=request.user)

    total_products = products.count()
    total_value = sum(product.amount for product in products)

    order_items = OrderItem.objects.filter(seller=request.user).select_related("order", "product").order_by("-order__created_at")

    return render(request, "dashboard.html", {
        "products": products,
        "total_products": total_products,
        "total_value": total_value,
        "order_items": order_items,
    })

@login_required
def add_product(request):
    if request.method == "POST":
        Product.objects.create(
            seller=request.user,
            name=request.POST.get("name"),
            category=request.POST.get("category"),
            amount=request.POST.get("amount"),
            description=request.POST.get("description"),
            condition=request.POST.get("condition"),
            image=request.FILES.get("image"),
        )
        return redirect("seller_dashboard")

    return render(request, "product_form.html")


@login_required
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
        return redirect("seller_dashboard")

    return render(request, "product_form.html", {"product": product})


# =========================
# STATIC PAGES
# =========================

def terms_view(request):
    return render(request, "terms.html")
def increase_cart_item(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + 1

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def decrease_cart_item(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def remove_cart_item(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def privacy_view(request):
    return render(request, "privacy.html")