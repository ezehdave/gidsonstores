from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

from django.utils import timezone

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=250, null=True)
    last_name = models.CharField(max_length=250, null=True)
    email = models.EmailField(max_length=250, null=True)

    def __str__(self):
      return self.user.email if self.user else "Guest Customer"


class ProductType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class RegionCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=200)
    product_type =models.ForeignKey(ProductType, on_delete=models.CASCADE, max_length=50,null=True, blank=True)
    price = models.FloatField()
    product_brifing = models.TextField(max_length=50,null=True, blank=True)
    country_categories = models.ManyToManyField(RegionCategory, related_name="posts")  # Many-to-Many Relationship
    image = models.ImageField(upload_to="images", null=True,blank=True)

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url =self.image.url
        except:
            url =""
        return url



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    create_account = models.BooleanField(default=False)
    order_notes = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Changed from FloatField to DecimalField
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.first_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Changed from FloatField to DecimalField

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"





class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage (e.g., 10 for 10%)
    min_cart_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Minimum cart total to apply
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        """Checks if the coupon is valid (not expired and active)"""
        return self.is_active and (self.expires_at is None or self.expires_at > timezone.now())

    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coupon')


