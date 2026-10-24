from django.contrib import admin

from .models import Profile, UserOTP


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "designation", "dept", "contact_number"]
    list_filter = ["designation", "dept"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "user__email"]


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
