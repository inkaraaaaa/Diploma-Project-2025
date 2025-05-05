# vacancies/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
]
