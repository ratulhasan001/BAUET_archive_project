from django.contrib import admin
from .models import Department


class DepartmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name',)}
    list_display = ['name', 'slug']

admin.site.register(Department, DepartmentAdmin)