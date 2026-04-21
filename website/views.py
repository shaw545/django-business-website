from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import ContactMessage, Product, Order
from .forms import SellerRegistrationForm, ProductForm


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'services.html')


def portfolio(request):
    return render(request, 'portfolio.html')


def products(request):
    products = Product.objects.filter(available=True).order_by('-created_at')
    return render(request, 'products.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    return render(request, 'product_detail.html', {'product': product})


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
    seller_total_earnings = seller_orders.aggregate(total=Sum('seller_earning'))['total'] or Decimal('0.00')
    platform_total_fees = seller_orders.aggregate(total=Sum('platform_fee_amount'))['total'] or Decimal('0.00')

    return render(request, 'seller_dashboard.html', {
        'seller_products': seller_products,
        'seller_orders': seller_orders,
        'total_products': total_products,
        'total_orders': total_orders,
        'seller_total_earnings': seller_total_earnings,
        'platform_total_fees': platform_total_fees,
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


def seller_logout(request):
    logout(request)
    return redirect('home')