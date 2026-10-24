from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "department", "year", "is_approved"]
    list_filter = ["is_approved", "department", "year"]
    list_editable = ["is_approved"]
    search_fields = ["title", "content"]
    filter_horizontal = ["authors", "supervisors"]
    actions = ["approve"]

    @admin.action(description="Approve selected posts")
    def approve(self, request, queryset):
        queryset.update(is_approved=True)
