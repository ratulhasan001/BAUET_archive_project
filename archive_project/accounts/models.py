from django.db import models
from django.contrib.auth.models import User
from .constants import DESIGNATION, DEPARTMENT
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE,default=None)
    designation = models.CharField(max_length=100, choices=DESIGNATION)
    dept = models.CharField(max_length=200, choices=DEPARTMENT,default=None,null=True, blank=True)
    contact_number = models.CharField(max_length=11,default=None,null=True,blank=True)
    address = models.CharField(max_length=200,default=None,null=True,blank=True)
    image = models.ImageField(upload_to='accounts/media/images/', default=None)
    def __str__(self):
        return self.user.username
    

class UserOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField()

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=10)
