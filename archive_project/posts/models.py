from django.db import models
from departments.models import Department
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from departments.models import Department

from taggit.models import TagBase, GenericTaggedItemBase

from slugify import slugify

class CustomTag(TagBase):
    slug = models.SlugField(unique=True, max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(CustomTag, self).save(*args, **kwargs)

class CustomTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(CustomTag, related_name="tagged_items", on_delete=models.CASCADE)

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    authors = models.ManyToManyField(User, related_name='posts')
    supervisors = models.ManyToManyField(User, related_name='supers')
    year = models.IntegerField(default=2018)
    file = models.FileField(upload_to='posts/media/uploads')
    is_approved = models.BooleanField(default=False)
    tags = TaggableManager(through=CustomTaggedItem)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,default=None)

    def __str__(self):
        return self.title

    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=30)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True) 
    
    def __str__(self):
        return f"Comments by {self.name}"
    
    
class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    posts = models.ManyToManyField(Post, related_name='wishlisted_by')

    def __str__(self):
        return f"{self.user.username}'s Wishlist"