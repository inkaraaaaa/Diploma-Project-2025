from django.contrib import admin
from .models import HRCompany, HRCompanyRequest, Interview

# Register your models here.

@admin.register(HRCompany)
class HRCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'city', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'city', 'created_at')
    search_fields = ('name', 'user__email')

@admin.register(HRCompanyRequest)
class HRCompanyRequestAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'hr_email', 'is_reviewed', 'is_approved', 'submitted_at')
    list_filter = ('is_reviewed', 'is_approved', 'city')
    search_fields = ('company_name', 'hr_email')

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'date', 'time', 'format', 'location')
    list_filter = ('format', 'date')
    search_fields = ('application__student__email', 'location')
