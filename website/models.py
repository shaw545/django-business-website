
from django.db import models

class ContactMessage(models.Model):
    SERVICE_CHOICES = [
        ('Accounting Support', 'Accounting Support'),
        ('Data Analytics', 'Data Analytics'),
        ('Business Solutions', 'Business Solutions'),
        ('General Inquiry', 'General Inquiry'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    service_interest = models.CharField(max_length=100, choices=SERVICE_CHOICES, default='General Inquiry')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.service_interest}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name