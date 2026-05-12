from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Product, Order, OrderItem, SellerProfile
from .models import Product, ProductColor, ProductImage

# =========================
# PUBLIC PAGES
# =========================

def home(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category=category)

    categories = [
        "Electronics",
        "Fashion & Clothing",
        "Home & Living",
        "Beauty & Personal Care",
        "Sports",
        "Other",
    ]

    return render(request, "home.html", {
        "products": products,
        "query": query,
        "categories": categories,
        "selected_category": category,
    })
def products_view(request):
    query = request.GET.get("q", "")

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, "products.html", {
        "products": products,
        "query": query,
    })

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

    return render(request, "cart.html", {
        "products": products,
        "total": total,
    })


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


# =========================
# CHECKOUT / ORDER
# =========================

def checkout_view(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0
    seller_profile = None

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        product.quantity = quantity
        product.subtotal = product.amount * quantity
        total += product.subtotal
        products.append(product)

    if products:
        first_product = products[0]
        seller_profile = SellerProfile.objects.filter(user=first_product.seller).first()
    if request.method == "POST":
        order = Order.objects.create(
            buyer_name=request.POST.get("buyer_name"),
            buyer_phone=request.POST.get("buyer_phone"),
            buyer_email=request.POST.get("buyer_email"),
            buyer_address=request.POST.get("buyer_address"),
            payment_method=request.POST.get("payment_method"),
            total_amount=total,
        )

        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                seller=product.seller,
                quantity=product.quantity,
                price=product.amount,
            )

        request.session["cart"] = {}
        request.session["last_order_id"] = order.id
        return redirect("order_confirmation")

    return render(request, "checkout.html", {
        "products": products,
        "total": total,
        "seller_profile": seller_profile,
    })
def order_confirmation(request):
    order_id = request.session.get("last_order_id")
    order = None

    if order_id:
        order = get_object_or_404(Order, id=order_id)

    return render(request, "order_confirmation.html", {
        "order": order,
    })


# =========================
# AUTH
# =========================

def register(request):
    if request.method == "POST":
        seller_type = request.POST.get("seller_type")

        if seller_type == "business":
            username = request.POST.get("username_business")
        else:
            username = request.POST.get("username")

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        email = request.POST.get("email", "")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")

        if not username:
            messages.error(request, "Username is required")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another username.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        SellerProfile.objects.create(
            user=user,
            seller_type=seller_type,
            business_name=request.POST.get("business_name", ""),
            business_address=request.POST.get("business_address", ""),
            business_logo=request.FILES.get("business_logo"),
            phone=request.POST.get("phone", ""),
            orange_number=request.POST.get("orange_number", ""),
            afri_number=request.POST.get("afri_number", ""),
        )

        messages.success(request, "Seller account created successfully.")
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

    order_items = OrderItem.objects.filter(
        seller=request.user
    ).select_related("order", "product").order_by("-order__created_at")

    return render(request, "dashboard.html", {
        "products": products,
        "total_products": total_products,
        "total_value": total_value,
        "order_items": order_items,
    })

@login_required
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        amount = request.POST.get("amount")
        category = request.POST.get("category")
        condition = request.POST.get("condition")
        image = request.FILES.get("image")
        extra_images = request.FILES.getlist("extra_images")
        extra_images = extra_images[:15]

        product = Product.objects.create(
            seller=request.user,
            name=name,
            description=description,
            amount=amount,
            category=category,
            condition=condition,
            image=image,
        )

        # Save colors
        colors_text = request.POST.get("colors", "")
        color_list = [c.strip() for c in colors_text.split(",") if c.strip()]

        color_objects = []
        for color_name in color_list:
            color_obj = ProductColor.objects.create(
                product=product,
                color_name=color_name
            )
            color_objects.append(color_obj)

        # Save multiple gallery images
        gallery_images = request.FILES.getlist("gallery_images")

        for gallery_image in gallery_images:
            ProductImage.objects.create(
                product=product,
                image=gallery_image,
                angle="other"
            )

        return redirect("seller_dashboard")

    return render(request, "add_product.html")

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

        if not product.seller:
            product.seller = request.user

        product.save()

        return redirect("seller_dashboard")

    return render(request, "product_form.html", {
        "product": product,
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == "POST":
        product.delete()
        return redirect("seller_dashboard")

    return render(request, "delete_product.html", {
        "product": product,
    })

def seller_store(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)
    products = Product.objects.filter(seller=seller)

    return render(request, "seller_store.html", {
        "seller": seller,
        "products": products,
    })

def seller_products(request, seller_id):
    seller = User.objects.get(id=seller_id)
    products = Product.objects.filter(seller=seller)

    return render(request, "seller_products.html", {
        "seller": seller,
        "products": products,
    })

# =========================
# STATIC PAGES
# =========================

def terms_view(request):
    return render(request, "terms.html")


def privacy_view(request):
    return render(request, "privacy.html")