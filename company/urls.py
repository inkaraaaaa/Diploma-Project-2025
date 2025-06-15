from django.urls import path
from . import views

urlpatterns = [
    path('hr/register/', views.hr_register_email, name='hr_register_email'),
    path('hr/login/', views.hr_login, name='hr_login'),
    path('hr/register/info/', views.hr_register_info, name='hr_register_info'),
    path('hr/register/complete/', views.hr_register_complete, name='hr_register_complete'),
    path('hr/final-register/', views.hr_register_user, name='hr_register_user'),
    path('hr/final-register/company/', views.hr_register_company, name='hr_register_company'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/internships/', views.internship_list, name='hr_internship_list'),
    path('hr/internships/add/', views.add_internship, name='hr_add_internship'),
    path('hr/internships/<int:pk>/applicants/', views.application_detail, name='hr_application_detail'),
    path('hr/download-cv/<int:user_id>/', views.download_cv, name='hr_download_cv'),
    path('hr/applicant/<int:application_id>/', views.applicant_detail, name='hr_applicant_detail'),
    path('admin_panel/hr-requests/', views.hr_requests_list, name='hr_requests_list'),
    path('admin_panel/hr-requests/<int:pk>/approve/', views.approve_hr_request, name='approve_hr_request'),
    path('admin_panel/hr-requests/<int:pk>/reject/', views.reject_hr_request, name='reject_hr_request'),
    path('admin_panel/hr-requests/<int:pk>/', views.hr_request_detail, name='hr_request_detail'),
    path('hr/save-interview/', views.save_interview, name='save_interview'),
    path('hr/reject-application/', views.reject_application, name='reject_application'),
    path('hr/internships/', views.internship_list, name='hr_internship_list'),
    path('internships/edit/<int:pk>/', views.edit_internship, name='hr_edit_internship'),
    path('internships/delete/<int:pk>/', views.delete_internship, name='hr_delete_internship'),

]