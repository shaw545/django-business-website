from django.db import models
from django.contrib.auth.models import User


class SellerProfile(models.Model):
    SELLER_TYPE_CHOICES = [
        ("personal", "Personal Seller"),
        ("business", "Business Seller"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    seller_type = models.CharField(max_length=20, choices=SELLER_TYPE_CHOICES, default="personal")
    business_name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=30)
    orange_number = models.CharField(max_length=30, blank=True, null=True)
    afri_number = models.CharField(max_length=30, blank=True, null=True)
    business_address = models.CharField(max_length=255, blank=True, null=True)
    business_logo = models.ImageField(upload_to="seller_logos/", blank=True, null=True)

    def display_name(self):
        if self.seller_type == "business" and self.business_name:
            return self.business_name
        return self.user.get_full_name() or self.user.username

    def __str__(self):
        return self.display_name()


class Product(models.Model):
    CONDITION_CHOICES = [
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Fair/Damaged", "Fair/Damaged"),
    ]

    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default="Good")
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_CHOICES = [
        ("pay_on_delivery", "Pay on Delivery"),
        ("mobile_money", "Mobile Money"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("payment_received", "Payment Received"),
        ("out_for_delivery", "Out for Delivery"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    buyer_name = models.CharField(max_length=200)
    buyer_phone = models.CharField(max_length=50)
    buyer_email = models.EmailField(blank=True, null=True)
    buyer_address = models.TextField()

    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.buyer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product} x {self.quantity}"

class SellerRating(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    buyer_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.username} - {self.rating} stars"