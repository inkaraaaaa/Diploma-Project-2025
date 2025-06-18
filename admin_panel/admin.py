from django.contrib import admin
from .models import AdminUser

# Register your models here.

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'phone')
    readonly_fields = ('last_login',)
