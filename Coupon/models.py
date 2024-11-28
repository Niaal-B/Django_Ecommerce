from django.db import models

# Create your models here.
class Coupon(models.Model):
    code  =  models.CharField(max_length=30,unique=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2) 
    min_purchase_amount = models.DecimalField(max_digits=10,decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    created_at = models.DateField(auto_now_add=True)
    