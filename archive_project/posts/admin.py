from django.contrib import admin

from .models import Comment, CustomTag, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "department", "year", "is_approved"]
    list_filter = ["is_approved", "department", "year"]
    list_editable = ["is_approved"]
    search_fields = ["title", "content"]
    filter_horizontal = ["authors", "supervisors"]
    actions = ["approve", "unapprove"]

    @admin.action(description="Approve selected posts")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Mark selected posts as pending")
    def unapprove(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(CustomTag)
class CustomTagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["name", "post", "created_on"]
