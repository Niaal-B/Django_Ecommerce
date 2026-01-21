from django.db import models
from django.core.files.storage import default_storage
from django.conf import settings
from Categories.models import Category

def get_cloudinary_storage():
    """Get Cloudinary storage if configured, otherwise use default"""
    storage_class = getattr(settings, 'DEFAULT_FILE_STORAGE', None)
    if storage_class and 'cloudinary' in storage_class.lower():
        from cloudinary_storage.storage import MediaCloudinaryStorage
        return MediaCloudinaryStorage()
    return default_storage

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()  
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)  # Adjusted precision
    offer = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # Increased precision
    color = models.CharField(max_length=50, null=True, blank=True)
    # Explicitly use Cloudinary storage if configured
    image1 = models.ImageField(upload_to='products/', null=True, storage=get_cloudinary_storage)
    image2 = models.ImageField(upload_to='products/', null=True, blank=True, storage=get_cloudinary_storage)
    image3 = models.ImageField(upload_to='products/', null=True, blank=True, storage=get_cloudinary_storage)
    created_at = models.DateTimeField(auto_now_add=True)
    is_listed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class SizeVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='size_variants')
    size = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.size}"
