from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    price_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_sle = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    image = CloudinaryField("image", folder="yusuf_products", blank=True, null=True)

    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image = CloudinaryField("image", folder="yusuf_products/gallery", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField()

    quantity = models.PositiveIntegerField(default=1)
    currency = models.CharField(max_length=10, default="SLE")

    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    platform_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    platform_fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    seller_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=30, default="Pending Verification")
    payment_method = models.CharField(max_length=100, blank=True, default="Manual Payment")
    payment_reference = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True)
    service_interest = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PayoutRequest(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected"),
        ],
        default="Pending",
    )

    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.username} - {self.amount}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=100)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars"