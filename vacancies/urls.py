# vacancies/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('vacancies/', views.job_list, name='vacancies'),
    path('jobs/', views.success_view, name='job_list'),
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
]
