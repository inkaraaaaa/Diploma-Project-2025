from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255, default="Default Location")  # Сделано nullable
    description = models.TextField()
    prize_info = models.CharField(max_length=100)
    team_info = models.CharField(max_length=100)
    registration_deadline = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title

