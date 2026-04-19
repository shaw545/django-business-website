from django.shortcuts import render
from .models import ContactMessage

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')

def portfolio(request):
    return render(request, 'portfolio.html')

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
        success = True

    return render(request, 'contact.html', {'success': success})