from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = sum(item.quantity for item in cart.items.all())

    context = {
        "categories": categories,
        "products": products,
        "cart_count": cart_count,
    }
    return render(request, "shop/product_list.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = sum(item.quantity for item in cart.items.all())

    return render(request, "shop/product_detail.html", {
        "product": product,
        "cart_count": cart_count,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_authenticated:
        return redirect("login")

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_authenticated:
        return redirect("login")

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("checkout")