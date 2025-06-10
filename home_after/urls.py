from django.urls import path
from .views import job_list,job_detail, vacancies_view, afisha2_view, events_view, create_event, advice_view

urlpatterns = [
    path('home-after/', job_list, name='home-after'),
    path('jobs/<int:job_id>/', job_detail, name='job_detail'),
    path('vacancies/', vacancies_view, name='vacancies'),
    path('afisha2/<int:id>/', afisha2_view, name='afisha2'),
    path('events', events_view, name='events'),
    path('create/', create_event, name='create-event'),
    path('advice/', advice_view, name='advices')
]
