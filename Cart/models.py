from django.db import models
from django.contrib.auth.models import User
from Products.models import Product,SizeVariant


class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
     
    def __str__(self):
        return f'Cart of {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    size = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.quantity} of {self.product.name} ({self.size}) in cart of {self.cart.user.username}'

    def total_price(self):
        return self.quantity * self.product.price

