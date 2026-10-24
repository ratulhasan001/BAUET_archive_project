from django.contrib.auth.models import User
from django.db import models

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
