from django.db import models
from users.models import UserProfile

class Workers(models.Model):
    name = models.CharField(max_length=20, blank=False)
    second_name = models.CharField(max_length = 35, blank=False)
    salary = models.IntegerField(default=0)
    def __str__(self):
        return f'{self.second_name} {self.name}'
    
class Student(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    cities = models.ManyToManyField(City, through='CompanyCity')
    overview = models.TextField()
    partnership = models.TextField()

    def __str__(self):
        return self.name

class CompanyCity(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.company.name} - {self.city.name}"
    
class Internship(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="internships")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="interns")
    position = models.CharField(max_length=100)  # Должность стажера
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.position} at {self.company.name}"
    
class Comment(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)  # Связываем с пользователем
    text = models.TextField()
    rating = models.PositiveIntegerField(default=1)  # Оценка от 1 до 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.internship.company.name}"
        


