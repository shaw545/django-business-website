
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from .models import ContactMessage, Product

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