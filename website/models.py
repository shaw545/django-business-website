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