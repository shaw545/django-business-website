from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import SellerRegistrationForm, ProductForm, ProductReviewForm
from .models import (
    Category,
    Product,
    ProductImage,
    Order,
    ContactMessage,
    PayoutRequest,
    ProductReview,
)


def _get_cart(request):
    return request.session.get("cart", [])


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def _cart_count(request):
    cart = _get_cart(request)
    return sum(int(item.get("quantity", 1)) for item in cart)


def _build_cart_rows(request):
    cart = _get_cart(request)
    cart_rows = []
    grand_total = Decimal("0.00")

    for item in cart:
        product = Product.objects.filter(
            id=item.get("product_id"),
            available=True
        ).first()

        if not product:
            continue

        quantity = int(item.get("quantity", 1))
        unit_price = Decimal(product.price_sle)
        row_total = unit_price * Decimal(quantity)
        grand_total += row_total

        cart_rows.append({
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "row_total": row_total,
        })

    return cart_rows, grand_total


def home(request):
    products = Product.objects.filter(available=True).order_by("-created_at")[:8]
    categories = Category.objects.all().order_by("name")

    return render(request, "home.html", {
        "products": products,
        "categories": categories,
    })


def products(request):
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    products_qs = Product.objects.filter(available=True).order_by("-created_at")

    if category_id:
        products_qs = products_qs.filter(category_id=category_id)

    if query:
        products_qs = products_qs.filter(name__icontains=query)

    categories = Category.objects.all().order_by("name")

    selected_category_name = ""
    if category_id:
        selected_category = Category.objects.filter(id=category_id).first()
        if selected_category:
            selected_category_name = selected_category.name

    return render(request, "products.html", {
        "products": products_qs,
        "categories": categories,
        "query": query,
        "selected_category": category_id,
        "selected_category_name": selected_category_name,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)

    gallery_images = ProductImage.objects.filter(
        product=product
    ).order_by("-id")

    reviews = ProductReview.objects.filter(product=product)
    review_form = ProductReviewForm()

    if request.method == "POST" and "submit_review" in request.POST:
        review_form = ProductReviewForm(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.save()
            messages.success(request, "Review submitted successfully.")
            return redirect("product_detail", product_id=product.id)

    return render(request, "product_detail.html", {
        "product": product,
        "gallery_images": gallery_images,
        "reviews": reviews,
        "review_form": review_form,
    })


def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html")


def portfolio(request):
    return render(request, "portfolio.html")


def terms_view(request):
    return render(request, "terms.html")


def privacy_view(request):
    return render(request, "privacy.html")


def contact(request):
    success = False

    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            company=request.POST.get("company"),
            service_interest=request.POST.get("service_interest"),
            message=request.POST.get("message"),
        )
        success = True

    return render(request, "contact.html", {
        "success": success,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)

    cart = _get_cart(request)
    found = False

    for item in cart:
        if item.get("product_id") == product.id:
            item["quantity"] = int(item.get("quantity", 1)) + 1
            found = True
            break

    if not found:
        cart.append({
            "product_id": product.id,
            "quantity": 1,
        })

    _save_cart(request, cart)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": _cart_count(request),
            "message": f"{product.name} added to cart.",
        })

    messages.success(request, "Product added to cart.")
    return redirect("cart")


def cart_view(request):
    cart_items, grand_total = _build_cart_rows(request)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "grand_total": grand_total,
        "cart_count": _cart_count(request),
    })


def update_cart_item(request, index):
    cart = _get_cart(request)

    if request.method == "POST" and 0 <= index < len(cart):
        quantity = int(request.POST.get("quantity", 1))

        if quantity <= 0:
            cart.pop(index)
        else:
            cart[index]["quantity"] = quantity

        _save_cart(request, cart)

    return redirect("cart")


def remove_cart_item(request, index):
    cart = _get_cart(request)

    if 0 <= index < len(cart):
        cart.pop(index)
        _save_cart(request, cart)

    return redirect("cart")


def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    success = False
    platform_fee_percent = Decimal(str(getattr(settings, "PLATFORM_FEE_PERCENT", 10)))

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        quantity = int(request.POST.get("quantity", 1))

        payment_method = request.POST.get("payment_method", "Manual Payment")
        payment_reference = request.POST.get("payment_reference", "")

        unit_price = Decimal(product.price_sle)
        total_amount = unit_price * Decimal(quantity)
        platform_fee_amount = (platform_fee_percent / Decimal("100")) * total_amount
        seller_earning = total_amount - platform_fee_amount

        Order.objects.create(
            product=product,
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            quantity=quantity,
            currency="SLE",
            unit_price=unit_price,
            total_amount=total_amount,
            platform_fee_percent=platform_fee_percent,
            platform_fee_amount=platform_fee_amount,
            seller_earning=seller_earning,
            payment_status="Pending Verification",
            payment_method=payment_method,
            payment_reference=payment_reference,
        )

        success = True

    return render(request, "checkout.html", {
        "product": product,
        "success": success,
        "platform_fee_percent": platform_fee_percent,
    })


def cart_checkout(request):
   