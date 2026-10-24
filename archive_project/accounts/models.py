from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .constants import DEPARTMENT, DESIGNATION


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE, default=None)
    designation = models.CharField(max_length=100, choices=DESIGNATION)
    dept = models.CharField(max_length=200, choices=DEPARTMENT, default=None, null=True, blank=True)
    contact_number = models.CharField(max_length=11, default=None, null=True, blank=True)
    address = models.CharField(max_length=200, default=None, null=True, blank=True)
    image = models.ImageField(upload_to="profile_images/", blank=True)

    def __str__(self):
        return self.user.username

    @property
    def initials(self):
        first = self.user.first_name[:1]
        last = self.user.last_name[:1]
        return (first + last).upper() or self.user.username[:2].upper()


class UserOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField()

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
