from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Product, SellerProfile
from django.contrib.auth.decorators import login_required


def products_view(request):
    products = Product.objects.all()
    return render(request, "products.html", {"products": products})

def home(request):
    products = Product.objects.all()
    return render(request, "home.html", {"products": products})

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

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # Save payment method
        request.session["payment_method"] = payment_method
        request.session.modified = True

        return redirect("order_confirmation")

    return render(request, "checkout.html", {
        "products": products,
        "total": total
    })

def register(request):
    if request.method == "POST":
        seller_type = request.POST.get("seller_type")
        business_name = request.POST.get("business_name")
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
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

        SellerProfile.objects.create(
            user=user,
            phone=phone,
            orange_number=request.POST.get("orange_number"),
       )
        SellerProfile.objects.create(
            user=user,
            seller_type=seller_type,
            business_name=business_name,
            phone=phone,
        )

        return redirect("login")

    return render(request, "register.html")


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    seller_name = "Seller"
    if product.seller:
        try:
            seller_name = product.seller.sellerprofile.display_name()
        except SellerProfile.DoesNotExist:
            seller_name = product.seller.get_full_name() or product.seller.username

    return render(request, "product_detail.html", {
        "product": product,
        "seller_name": seller_name,
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
def seller_dashboard(request):
    products = Product.objects.filter(seller=request.user)

    total_products = products.count()
    total_value = sum(product.amount for product in products)

    return render(request, "dashboard.html", {
        "products": products,
        "total_products": total_products,
        "total_value": total_value,
    })

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

        if not product.seller and request.user.is_authenticated:
            product.seller = request.user

        product.save()
        return redirect("seller_dashboard")

    return render(request, "product_form.html", {"product": product})

def terms_view(request):
    return render(request, "terms.html")


def privacy_view(request):
    return render(request, "privacy.html")
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
def order_confirmation(request):
    request.session["cart"] = {}
    request.session.modified = True
    return render(request, "order_confirmation.html")