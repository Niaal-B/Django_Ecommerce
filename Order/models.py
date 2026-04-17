from django.db import models

from Products.models import Product,SizeVariant
from django.db import models
from django.contrib.auth.models import User
from Account.models import Address  # Import Address model

class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valid_from = models.DateField()
    valid_to = models.DateField()
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.discount_value}"

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out For Delivery'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=50, default="pending")
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    return_reason = models.TextField(blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_cancellable(self):
        """Returns True if the order can be canceled by the user."""
        return self.status in ['pending', 'confirmed']
    @property
    def is_returnable(self):
        """Returns True if the order can be returned by the user (only if delivered)."""
        return self.status == 'delivered'

    def sync_items_status(self, new_status=None):
        """Synchronizes all OrderItems with the Order's status or a specific status."""
        target_status = new_status if new_status else self.status
        self.items.all().update(status=target_status)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=50, choices=Order.ORDER_STATUS_CHOICES, default='pending')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
 