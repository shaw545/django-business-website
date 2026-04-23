from django.db import models
from django.contrib.auth.models import User


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
    service_interest = models.CharField(
        max_length=100,
        choices=SERVICE_CHOICES,
        default='General Inquiry'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.service_interest}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price_sle = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery image for {self.product.name}"


class Order(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('SLE', 'Sierra Leone Leone'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='SLE')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    platform_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    platform_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    seller_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_reference = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.product.name}"


class PayoutRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Paid', 'Paid'),
        ('Rejected', 'Rejected'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.username} - {self.amount} - {self.status}"