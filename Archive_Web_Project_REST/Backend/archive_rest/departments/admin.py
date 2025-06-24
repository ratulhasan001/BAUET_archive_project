from django.contrib import admin
from .models import Department

class DepartmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',), }

admin.site.register(Department,DepartmentAdmin)
