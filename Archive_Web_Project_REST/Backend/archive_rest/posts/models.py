from django.contrib.auth.models import User
from django.db import models

from departments.models import Department


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    authors = models.ManyToManyField(User, related_name="posts")
    supervisors = models.ManyToManyField(User, related_name="supers", blank=True)
    year = models.IntegerField(default=2018)
    file = models.FileField(upload_to="uploads/")
    is_approved = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=None)

    class Meta:
        ordering = ["-year", "-id"]

    def __str__(self):
        return self.title

    def is_managed_by(self, user):
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return (
            self.authors.filter(pk=user.pk).exists()
            or self.supervisors.filter(pk=user.pk).exists()
        )
