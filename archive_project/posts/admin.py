from django.contrib import admin
from .models import Post, Comment, Wishlist, CustomTag

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_approved']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_approved:
            for author in obj.authors.all():
                # send_transaction_email(author, "Post Approved", "pa.html")
                pass

admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Wishlist)