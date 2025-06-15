from django.urls import path
from .views import job_list,job_detail, vacancies_view, afisha2_view

urlpatterns = [
    path('home-after/', job_list, name='home-after'),
    path('jobs/<int:job_id>/', job_detail, name='job_detail'),
    #path('vacancies/', vacancies_view, name='vacancies'),
    path('afisha2/<int:id>/', afisha2_view, name='afisha2'),
]
