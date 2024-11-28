from django.db import models
from django.contrib.auth.models import User
from Products.models import Product
# Create your models here.

class Wishlist(models.Model):
    user =  models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    size = models.CharField(max_length=10,default='S')

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.name}"
