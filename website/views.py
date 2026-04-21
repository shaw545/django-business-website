from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import ContactMessage, Category, Product, CartItem, Order, PayoutRequest
from .forms import SellerRegistrationForm, ProductForm

from .models import Product, Category

def home(request):
    products = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'categories': categories
    })

def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')


def portfolio(request):
    return render(request, 'portfolio.html')


def products(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products = Product.objects.filter(available=True).order_by('-created_at')

    if query:
        products = products.filter(name__icontains=query)

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'query': query or '',
        'selected_category': category_id or '',
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    return render(request, 'product_detail.html', {'product': product})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    currency = request.POST.get('currency', 'USD')

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        currency=currency,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, 'Product added to cart.')
    return redirect('cart')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    cart_rows = []
    grand_total = Decimal('0.00')

    for item in cart_items:
        unit_price = item.product.price_usd if item.currency == 'USD' else item.product.price_sle
        unit_price = Decimal(unit_price)
        row_total = unit_price * item.quantity
        grand_total += row_total

        cart_rows.append({
            'id': item.id,
            'product': item.product,
            'quantity': item.quantity,
            'currency': item.currency,
            'unit_price': unit_price,
            'row_total': row_total,
        })

    return render(request, 'cart.html', {
        'cart_items': cart_rows,
        'grand_total': grand_total,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    })


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()

    return redirect('cart')


@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    success = False
    platform_fee_percent = Decimal(str(settings.PLATFORM_FEE_PERCENT))

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        quantity = int(request.POST.get('quantity', 1))
        currency = request.POST.get('currency')

        unit_price = product.price_usd if currency == 'USD' else product.price_sle
        unit_price = Decimal(unit_price)
        total_amount = unit_price * Decimal(quantity)
        platform_fee_amount = (platform_fee_percent / Decimal('100')) * total_amount
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
            payment_status='Pending',
        )

        send_mail(
            subject=f'New Order for {product.name}',
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
            recipient_list=['info@yusufbusinesssolutions.com'],
            fail_silently=True,
        )

        success = True

    return render(request, 'checkout.html', {
        'product': product,
        'success': success,
        'platform_fee_percent': platform_fee_percent,
    })


@login_required
def cart_checkout(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    success = False
    platform_fee_percent = Decimal(str(settings.PLATFORM_FEE_PERCENT))

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        for item in cart_items:
            unit_price = item.product.price_usd if item.currency == 'USD' else item.product.price_sle
            unit_price = Decimal(unit_price)
            total_amount = unit_price * item.quantity
            platform_fee_amount = (platform_fee_percent / Decimal('100')) * total_amount
            seller_earning = total_amount - platform_fee_amount

            Order.objects.create(
                product=item.product,
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                quantity=item.quantity,
                currency=item.currency,
                unit_price=unit_price,
                total_amount=total_amount,
                platform_fee_percent=platform_fee_percent,
                platform_fee_amount=platform_fee_amount,
                seller_earning=seller_earning,
                payment_status='Pending',
            )

        cart_items.delete()
        success = True

        return render(request, 'cart_checkout.html', {
            'success': success,
            'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        })

    cart_rows = []
    grand_total = Decimal('0.00')

    for item in cart_items:
        unit_price = item.product.price_usd if item.currency == 'USD' else item.product.price_sle
        unit_price = Decimal(unit_price)
        row_total = unit_price * item.quantity
        grand_total += row_total

        cart_rows.append({
            'product': item.product,
            'quantity': item.quantity,
            'currency': item.currency,
            'unit_price': unit_price,
            'row_total': row_total,
        })

    return render(request, 'cart_checkout.html', {
        'cart_items': cart_rows,
        'grand_total': grand_total,
        'success': success,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    })


def contact(request):
    success = False

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        company = request.POST.get('company')
        service_interest = request.POST.get('service_interest')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            company=company,
            service_interest=service_interest,
            message=message
        )

        send_mail(
            subject=f'New Contact Form Submission from {name}',
            message=f"""
Name: {name}
Email: {email}
Company: {company}
Service Interest: {service_interest}

Message:
{message}
""",
            from_email=None,
            recipient_list=['info@yusufbusinesssolutions.com'],
            fail_silently=True,
        )

        success = True

    return render(request, 'contact.html', {'success': success})


def register(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('seller_dashboard')
    else:
        form = SellerRegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def seller_dashboard(request):
    seller_products = Product.objects.filter(seller=request.user).order_by('-created_at')
    seller_orders = Order.objects.filter(product__seller=request.user).order_by('-created_at')

    total_products = seller_products.count()
    total_orders = seller_orders.count()
    paid_orders = seller_orders.filter(payment_status='Paid')

    seller_total_earnings = paid_orders.aggregate(total=Sum('seller_earning'))['total'] or Decimal('0.00')
    seller_payouts = PayoutRequest.objects.filter(seller=request.user).order_by('-request_date')
    total_requested = seller_payouts.exclude(status='Rejected').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    available_balance = seller_total_earnings - total_requested
    if available_balance < 0:
        available_balance = Decimal('0.00')

    return render(request, 'seller_dashboard.html', {
        'seller_products': seller_products,
        'seller_orders': seller_orders,
        'total_products': total_products,
        'total_orders': total_orders,
        'seller_total_earnings': seller_total_earnings,
        'available_balance': available_balance,
        'seller_payouts': seller_payouts,
    })


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})


@login_required
def request_withdrawal(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, 'Enter a valid amount.')
            return redirect('seller_dashboard')

        paid_orders = Order.objects.filter(product__seller=request.user, payment_status='Paid')
        seller_total_earnings = paid_orders.aggregate(total=Sum('seller_earning'))['total'] or Decimal('0.00')

        seller_payouts = PayoutRequest.objects.filter(seller=request.user)
        total_requested = seller_payouts.exclude(status='Rejected').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        available_balance = seller_total_earnings - total_requested

        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero.')
        elif amount > available_balance:
            messages.error(request, 'Insufficient available balance.')
        else:
            PayoutRequest.objects.create(
                seller=request.user,
                amount=amount,
                status='Pending'
            )
            messages.success(request, 'Withdrawal request submitted successfully.')

    return redirect('seller_dashboard')


def seller_logout(request):
    logout(request)
    return redirect('home')