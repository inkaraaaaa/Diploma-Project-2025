from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class UserProfile(AbstractUser):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    university_course = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    cv = models.BinaryField(null=True, blank=True)
    languages = models.ManyToManyField(Language, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    is_hr = models.BooleanField(default=False)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="user_profiles",
        blank=True
    )

    groups = models.ManyToManyField(
        Group,
        related_name='userprofile_set',  # уникальное имя для обратной связи
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_languages_list(self):
        return self.languages.split(', ') if self.languages else []



class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.email}"

class Notification(models.Model):
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    interview = models.ForeignKey('company.Interview', on_delete=models.CASCADE, null=True, blank=True)

    def delete_old_notifications():
        threshold = timezone.now() - timedelta(days=30)
        Notification.objects.filter(created_at__lt=threshold).delete()


    def __str__(self):
        return f"Notification to {self.recipient.username}"
    





