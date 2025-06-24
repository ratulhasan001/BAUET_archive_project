from django.db import models
from departments.models import Department
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    authors = models.ManyToManyField(User, related_name='posts')
    supervisors = models.ManyToManyField(User, related_name='supers')
    year = models.IntegerField(default=2018)
    file = models.FileField(upload_to='posts/media/uploads')
    is_approved = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,default=None)

    def __str__(self):
        return self.title