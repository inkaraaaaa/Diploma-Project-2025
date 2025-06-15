from django.db import models
from django.conf import settings
from sendreview.models import City, Company

class HRCompany(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='media/company_logos/')
    employee_count = models.PositiveIntegerField()
    overview = models.TextField()
    city = models.ForeignKey('sendreview.City', on_delete=models.CASCADE)
    partnership = models.TextField(null=True, blank=True)       # ← если тебе нужно это поле
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    
class HRCompanyRequest(models.Model):
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_request_logos/', null=True, blank=True)
    overview = models.TextField()
    partnership = models.TextField()
    city = models.ForeignKey('sendreview.City', on_delete=models.CASCADE)
    employee_count = models.PositiveIntegerField()
    
    hr_name = models.CharField(max_length=255)
    hr_email = models.EmailField()
    
    is_reviewed = models.BooleanField(default=False)
    is_approved = models.BooleanField(null=True, blank=True)
    token = models.CharField(max_length=64, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} ({'Approved' if self.is_approved else 'Pending'})"

class Interview(models.Model):
    application = models.ForeignKey('vacancies.Application', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    format = models.CharField(max_length=10, choices=[('online', 'Online'), ('offline', 'Offline')])
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview for {self.application.student.get_full_name()} on {self.date} at {self.time}"
