from django.shortcuts import render, get_object_or_404, redirect
from .models import Product

# =========================
# HOME PAGE
# =========================
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


# =========================
# ALL PRODUCTS PAGE
# =========================
def products(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


# =========================
# PRODUCT DETAIL
# =========================
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


# =========================
# ADD TO CART
# =========================
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})

    if str(pk) in cart:
        cart[str(pk)] += 1
    else:
        cart[str(pk)] = 1

    request.session['cart'] = cart
    return redirect('cart')


# =========================
# CART VIEW
# =========================
def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for pk, quantity in cart.items():
        product = get_object_or_404(Product, pk=pk)

        product.quantity = quantity
        product.subtotal = product.price * quantity   # ✅ FIXED

        total += product.subtotal
        products.append(product)

    return render(request, 'cart.html', {
        'products': products,
        'total': total
    })


# =========================
# CHECKOUT
# =========================
def checkout_view(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for pk, quantity in cart.items():
        product = get_object_or_404(Product, pk=pk)

        product.quantity = quantity
        product.subtotal = product.price * quantity   # ✅ FIXED

        total += product.subtotal
        products.append(product)

    return render(request, 'checkout.html', {
        'products': products,
        'total': total
    })


# =========================
# CLEAR CART
# =========================
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')
def about(request):
    return render(request, "about.html")