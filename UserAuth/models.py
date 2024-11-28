from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def is_expired(self):
        return timezone.now() > self.expires_at


