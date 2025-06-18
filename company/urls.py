from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('hr/register/', views.hr_register_email, name='hr_register_email'),
    path('hr/login/', views.hr_login, name='hr_login'),
    path('hr/register/info/', views.hr_register_info, name='hr_register_info'),
    path('hr/register/complete/', views.hr_register_complete, name='hr_register_complete'),
    path('hr/final-register/', views.hr_register_user, name='hr_register_user'),
    path('hr/final-register/company/', views.hr_register_company, name='hr_register_company'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('hr/internships/<int:pk>/applicants/', views.application_detail, name='hr_application_detail'),
    path('admin/download-cv/<int:user_id>/', views.download_cv, name='admin_download_cv'),
    path('hr/applicant/<int:application_id>/', views.applicant_detail, name='hr_applicant_detail'),
    path('admin_panel/hr-requests/', views.hr_requests_list, name='hr_requests_list'),
    path('admin_panel/hr-requests/<int:pk>/approve/', views.approve_hr_request, name='approve_hr_request'),
    path('admin_panel/hr-requests/<int:pk>/reject/', views.reject_hr_request, name='reject_hr_request'),
    path('admin_panel/hr-requests/<int:pk>/', views.hr_request_detail, name='hr_request_detail'),
    path('hr/save-interview/', views.save_interview, name='save_interview'),
    path('hr/reject-application/', views.reject_application, name='reject_application'),
    path('hr/internships/', views.hr_vacancies_view, name='hr_vacancies'),
    path('hr/internships/add/', views.hr_add_internship, name='hr_add_internship'),
    path('hr/internships/<int:internship_id>/edit/', views.hr_edit_internship, name='hr_edit_internship'),
    path('hr/internships/delete/<int:pk>/', views.delete_internship, name='hr_delete_internship'),
    path('hr/internships/<int:pk>/applicants/', views.application_detail, name='hr_application_detail'),
    path('hr/accept-application/', views.accept_application, name='accept_application'),
    path('hr/profile/', views.hr_profile_view, name='hr_profile'),
    path('hr/profile/edit-company/', views.edit_company, name='hr_editcompany'),
    path('hr/change-password/', views.hr_change_password, name='hr_change_password'),
    path('logout/', LogoutView.as_view(next_page='hr_login'), name='logout'),
    path('hr/internships/<int:pk>/delete/', views.delete_internship, name='hr_delete_internship'),

]