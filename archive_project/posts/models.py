from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase

from departments.models import Department


class CustomTag(TagBase):
    slug = models.SlugField(unique=True, max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class CustomTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(CustomTag, related_name="tagged_items", on_delete=models.CASCADE)


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField("Abstract")
    authors = models.ManyToManyField(User, related_name="posts")
    supervisors = models.ManyToManyField(User, related_name="supers", blank=True)
    year = models.IntegerField(default=2018)
    file = models.FileField(upload_to="uploads/")
    is_approved = models.BooleanField(default=False)
    tags = TaggableManager(through=CustomTaggedItem, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=None)

    class Meta:
        ordering = ["-year", "-id"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("detail_post", args=[self.pk])

    @property
    def file_name(self):
        return self.file.name.rsplit("/", 1)[-1] if self.file else ""

    def can_manage(self, user):
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return (
            self.authors.filter(pk=user.pk).exists()
            or self.supervisors.filter(pk=user.pk).exists()
        )

    def can_view(self, user):
        return self.is_approved or self.can_manage(user)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=30)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment by {self.name}"


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wishlist")
    posts = models.ManyToManyField(Post, related_name="wishlisted_by")

    def __str__(self):
        return f"{self.user.username}'s wishlist"
