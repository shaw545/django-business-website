from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from .models import ContactMessage, Product, Order

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def products(request):
    products = Product.objects.filter(available=True)
    return render(request, 'products.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    return render(request, 'product_detail.html', {'product': product})

def checkout(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    success = False

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        quantity = int(request.POST.get('quantity', 1))
        currency = request.POST.get('currency')

        unit_price = product.price_usd if currency == 'USD' else product.price_sle
        total_amount = Decimal(unit_price) * quantity

        Order.objects.create(
            product=product,
            customer_name=customer_name,
            email=email,
            phone=phone,
            quantity=quantity,
            currency=currency,
            total_amount=total_amount
        )

        send_mail(
            subject=f'New Order for {product.name}',
            message=f"""
Customer: {customer_name}
Email: {email}
Phone: {phone}
Product: {product.name}
Quantity: {quantity}
Currency: {currency}
Total: {total_amount}
""",
            from_email=None,
            recipient_list=['info@yusufbusinesssolutions.com'],
            fail_silently=False,
        )

        success = True
        return render(request, 'checkout.html', {
            'product': product,
            'success': success
        })

    return render(request, 'checkout.html', {'product': product, 'success': success})

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
            fail_silently=False,
        )

        success = True

    return render(request, 'contact.html', {'success': success})