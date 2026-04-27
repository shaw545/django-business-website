from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem


# -------------------------------
# PRODUCT LIST (products.html)
# -------------------------------
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = sum(item.quantity for item in cart.items.all())

    return render(request, "products.html", {
        "products": products,
        "categories": categories,
        "cart_count": cart_count,
    })


# -------------------------------
# PRODUCT DETAIL (product_detail.html)
# -------------------------------
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = sum(item.quantity for item in cart.items.all())

    return render(request, "product_detail.html", {
        "product": product,
        "cart_count": cart_count,
    })


# -------------------------------
# ADD TO CART
# -------------------------------
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


# -------------------------------
# BUY NOW
# -------------------------------
def buy_now(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("checkout")


# -------------------------------
# CART PAGE
# -------------------------------
def cart_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    total = sum(item.product.price * item.quantity for item in items)

    return render(request, "cart.html", {
        "cart": cart,
        "items": items,
        "total": total,
    })


# -------------------------------
# CHECKOUT
# -------------------------------
def checkout(request):
    if not request.user.is_authenticated:
        return redirect("login")

    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    total = sum(item.product.price * item.quantity for item in items)

    if request.method == "POST":
        # Later we will save order + buyer info
        cart.items.all().delete()
        return redirect("product_list")

    return render(request, "checkout.html", {
        "items": items,
        "total": total,
    })