from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from .models import ContactMessage, Category, Product, ProductImage, Order, PayoutRequest
from .forms import SellerRegistrationForm, ProductForm


def _get_cart(request):
    return request.session.get("cart", [])


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


def _build_cart_rows(request):
    cart = _get_cart(request)
    cart_rows = []
    grand_total = Decimal("0.00")

    for item in cart:
        product = Product.objects.filter(id=item["product_id"], available=True).first()
        if not product:
            continue

        quantity = int(item.get("quantity", 1))
        currency = item.get("currency", "SLE")

        unit_price = product.price_sle if currency == "SLE" else product.price_usd
        unit_price = Decimal(unit_price)
        row_total = unit_price * quantity
        grand_total += row_total

        cart_rows.append({
            "product": product,
            "quantity": quantity,
            "currency": currency,
            "unit_price": unit_price,
            "row_total": row_total,
        })

    return cart_rows, grand_total


def home(request):
    products = Product.objects.filter(available=True).order_by("-created_at")[:8]
    categories = Category.objects.all()

    return render(request, "home.html", {
        "products": products,
        "categories": categories,
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


def products(request):
    query = request.GET.get("q")
    category_id = request.GET.get("category")

    products_qs = Product.objects.filter(available=True).order_by("-created_at")

    if query:
        products_qs = products_qs.filter(name__icontains=query)

    if category_id:
        products_qs = products_qs.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, "products.html", {
        "products": products_qs,
        "categories": categories,
        "query": query or "",
        "selected_category": category_id or "",
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    gallery_images = product.gallery_images.all()
    return render(request, "product_detail.html", {
        "product": product,
        "gallery_images": gallery_images,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)

    cart = _get_cart(request)

    found = False
    for item in cart:
        if item["product_id"] == product.id and item["currency"] == "SLE":
            item["quantity"] += 1
            found = True
            break

    if not found:
        cart.append({
            "product_id": product.id,
            "quantity": 1,
            "currency": "SLE",
        })

    _save_cart(request, cart)
    messages.success(request, "Product added to cart.")
    return redirect("cart")


def cart_view(request):
    cart_items, grand_total = _build_cart_rows(request)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "grand_total": grand_total,
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
        messages.info(request, "Item removed from cart.")

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
        currency = "SLE"

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
            currency=currency,
            unit_price=unit_price,
            total_amount=total_amount,
            platform_fee_percent=platform_fee_percent,
            platform_fee_amount=platform_fee_amount,
            seller_earning=seller_earning,
            payment_status="Pending",
        )

        send_mail(
            subject=f"New Order for {product.name}",
            message=f"""
Customer: {customer_name}
Email: {email}
Phone: {phone}
Address: {address}

Product: {product.name}
Quantity: {quantity}
Currency: {currency}
Unit Price: {unit_price}
Total Amount: {total_amount}
Platform Fee ({platform_fee_percent}%): {platform_fee_amount}
Seller Earning: {seller_earning}
""",
            from_email=None,
            recipient_list=["info@yusufbusinesssolutions.com"],
            fail_silently=True,
        )

        success = True

    return render(request, "checkout.html", {
        "product": product,
        "success": success,
        "platform_fee_percent": platform_fee_percent,
    })


def cart_checkout(request):
    cart_items, grand_total = _build_cart_rows(request)
    success = False
    platform_fee_percent = Decimal(str(getattr(settings, "PLATFORM_FEE_PERCENT", 10)))

    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        for item in cart_items:
            product = item["product"]
            quantity = item["quantity"]
            currency = "SLE"
            unit_price = Decimal(product.price_sle)
            total_amount = unit_price * quantity

            platform_fee_amount = (platform_fee_percent / Decimal("100")) * total_amount
            seller_earning = total_amount - platform_fee_amount

            Order.objects.create(
                product=product,
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                quantity=quantity,
                currency=currency,
                unit_price=unit_price,
                total_amount=total_amount,
                platform_fee_percent=platform_fee_percent,
                platform_fee_amount=platform_fee_amount,
                seller_earning=seller_earning,
                payment_status="Pending",
            )

        _save_cart(request, [])
        success = True

        return render(request, "cart_checkout.html", {
            "success": success,
            "cart_items": [],
            "grand_total": Decimal("0.00"),
        })

    return render(request, "cart_checkout.html", {
        "cart_items": cart_items,
        "grand_total": grand_total,
        "success": success,
    })


def contact(request):
    success = False

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        company = request.POST.get("company")
        service_interest = request.POST.get("service_interest")
        message = request.POST.get("message")

        ContactMessage.objects.create(
            name=name,
            email=email,
            company=company,
            service_interest=service_interest,
            message=message,
        )

        send_mail(
            subject=f"New Contact Form Submission from {name}",
            message=f"""
Name: {name}
Email: {email}
Company: {company}
Service Interest: {service_interest}

Message:
{message}
""",
            from_email=None,
            recipient_list=["info@yusufbusinesssolutions.com"],
            fail_silently=True,
        )

        success = True

    return render(request, "contact.html", {"success": success})


def register(request):
    if request.method == "POST":
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data.get("first_name", "")
            user.last_name = form.cleaned_data.get("last_name", "")
            user.save()
            login(request, user)
            messages.success(request, "Seller registration successful.")
            return redirect("seller_dashboard")
    else:
        form = SellerRegistrationForm()

    return render(request, "register.html", {"form": form})


@login_required
def seller_dashboard(request):
    seller_products = Product.objects.filter(seller=request.user).order_by("-created_at")
    seller_orders = Order.objects.filter(product__seller=request.user).order_by("-created_at")

    total_products = seller_products.count()
    total_orders = seller_orders.count()

    paid_orders = seller_orders.filter(payment_status="Paid")
    seller_total_earnings = paid_orders.aggregate(total=Sum("seller_earning"))["total"] or Decimal("0.00")

    seller_payouts = PayoutRequest.objects.filter(seller=request.user).order_by("-request_date")
    total_requested = seller_payouts.exclude(status="Rejected").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    available_balance = seller_total_earnings - total_requested
    if available_balance < 0:
        available_balance = Decimal("0.00")

    return render(request, "seller_dashboard.html", {
        "seller_products": seller_products,
        "seller_orders": seller_orders,
        "total_products": total_products,
        "total_orders": total_orders,
        "seller_total_earnings": seller_total_earnings,
        "available_balance": available_balance,
        "seller_payouts": seller_payouts,
    })


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        extra_files = request.FILES.getlist("extra_images")

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            for image_file in extra_files:
                ProductImage.objects.create(product=product, image=image_file)

            messages.success(request, "Product added successfully.")
            return redirect("seller_dashboard")
    else:
        form = ProductForm()

    return render(request, "add_product.html", {"form": form, "page_title": "Add Product"})


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        extra_files = request.FILES.getlist("extra_images")

        if form.is_valid():
            form.save()

            for image_file in extra_files:
                ProductImage.objects.create(product=product, image=image_file)

            messages.success(request, "Product updated successfully.")
            return redirect("seller_dashboard")
    else:
        form = ProductForm(instance=product)

    return render(request, "edit_product.html", {
        "form": form,
        "product": product,
        "gallery_images": product.gallery_images.all(),
        "page_title": "Edit Product",
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("seller_dashboard")

    return render(request, "delete_product.html", {"product": product})


@login_required
def delete_gallery_image(request, image_id):
    gallery_image = get_object_or_404(ProductImage, id=image_id, product__seller=request.user)
    product_id = gallery_image.product.id
    gallery_image.delete()
    messages.success(request, "Gallery image deleted.")
    return redirect("edit_product", product_id=product_id)


@login_required
def request_withdrawal(request):
    if request.method == "POST":
        amount = request.POST.get("amount")

        try:
            amount = Decimal(amount)
        except Exception:
            messages.error(request, "Enter a valid amount.")
            return redirect("seller_dashboard")

        paid_orders = Order.objects.filter(product__seller=request.user, payment_status="Paid")
        seller_total_earnings = paid_orders.aggregate(total=Sum("seller_earning"))["total"] or Decimal("0.00")

        seller_payouts = PayoutRequest.objects.filter(seller=request.user)
        total_requested = seller_payouts.exclude(status="Rejected").aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        available_balance = seller_total_earnings - total_requested

        if amount <= 0:
            messages.error(request, "Amount must be greater than zero.")
        elif amount > available_balance:
            messages.error(request, "Insufficient available balance.")
        else:
            PayoutRequest.objects.create(
                seller=request.user,
                amount=amount,
                status="Pending",
            )
            messages.success(request, "Withdrawal request submitted successfully.")

    return redirect("seller_dashboard")


def seller_logout(request):
    logout(request)
    return redirect("home")