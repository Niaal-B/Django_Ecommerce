from django.db import models
from django.core.files.storage import default_storage
from django.conf import settings

def get_cloudinary_storage():
    """Get Cloudinary storage if configured, otherwise use default"""
    storage_class = getattr(settings, 'DEFAULT_FILE_STORAGE', None)
    if storage_class and 'cloudinary' in storage_class.lower():
        from cloudinary_storage.storage import MediaCloudinaryStorage
        return MediaCloudinaryStorage()
    return default_storage

class Category(models.Model):
    category_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_listed = models.BooleanField(default=False)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, storage=get_cloudinary_storage) 
    def __str__(self):
        return self.category_name
