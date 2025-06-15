from django.db import models
from sendreview.models import Company
from users.models import UserProfile
from django.utils import timezone
from company.models import HRCompany

class JobListing(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
        ('expired', 'Expired'),
    ]

    title = models.CharField(max_length=256)
    description = models.TextField()
    job_type = models.CharField(max_length=50)
    experience_required = models.CharField(max_length=50)
    level = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    course = models.CharField(max_length=100, default='None')

    hr_company = models.ForeignKey(HRCompany, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    about_role = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)

    start_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open'
    )

    def __str__(self):
        return self.title
    
    def update_status_if_needed(self):
        today = timezone.now().date()

        if self.status == 'pending' and self.start_date and today >= self.start_date:
            self.status = 'open'
            self.save()

        if self.status == 'open' and self.deadline and today > self.deadline:
            self.status = 'expired'
            self.save()

    def save(self, *args, **kwargs):
        today = timezone.now().date()  # Получаем текущую дату

        if self.status == 'pending' and self.start_date and today >= self.start_date:
            self.status = 'open'

        if self.status == 'open' and self.deadline and today > self.deadline:
            self.status = 'expired'

        super().save(*args, **kwargs)
    
class Application(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)
    invited_to_interview = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student.email} → {self.job.title}"
