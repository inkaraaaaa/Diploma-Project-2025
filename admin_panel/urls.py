from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import custom_login, custom_logout
from .views import admin_panel, get_dashboard_data
from .views import students_list
from .views import unread_messages_count, mark_messages_read, unread_messages_details, delete_message
from .views import company_list, company_edit, company_delete, company_add
from .views import job_listing_list, job_listing_edit, job_listing_add, job_listing_delete
from .views import application_list, application_detail, export_applicants_csv, download_cv
from .views import internship_list, internship_add, internship_edit, internship_delete
from .views import add_city, stats_dashboard

urlpatterns = [
    path('adminlogin/', custom_login, name='adminlogin'),
     path('adminlogout/', custom_logout, name='adminlogout'),
    path("admin_panel/", admin_panel, name="admin_panel"),
    path('api/dashboard-data/', get_dashboard_data, name='dashboard-data'),
    path("api/delete-message/<int:message_id>/", delete_message, name="delete_message"),
    path('admin_panel/students/', students_list, name='students_list'),
    path('admin_panel/companies/', company_list, name='company_list'),
    path('admin_panel/companies/edit/<int:pk>/', company_edit, name='company_edit'),
    path('admin_panel/companies/delete/<int:pk>/', company_delete, name='company_delete'),
    path('admin_panel/companies/add/', company_add, name='company_add'),
    path('admin_panel/add_cities/', add_city, name='add_city'),
    path('admin_panel/internships/', job_listing_list, name='job_listing_list'),
    path('admin_panel/internships/add/', job_listing_add, name='job_listing_add'),
    path('admin_panel/internships/<int:job_id>/edit/', job_listing_edit, name='job_listing_edit'),
    path('admin_panel/internships/<int:job_id>/delete/', job_listing_delete, name='job_listing_delete'),
    path('admin_panel/doneinternships/', internship_list, name='internship_list'),
    path('admin_panel/doneinternships/add/', internship_add, name='internship_add'),
    path('admin_panel/doneinternships/edit/<int:pk>/', internship_edit, name='internship_edit'),
    path('admin_panel/doneinternships/delete/<int:pk>/', internship_delete, name='internship_delete'),
    path('admin_panel/applications/', application_list, name='application_list'),
    path('admin_panel/applications/<int:job_id>/', application_detail, name='application_detail'),
    path('admin_panel/applications/<int:job_id>/export/', export_applicants_csv, name='export_applicants_csv'),
    path('download-cv/<int:user_id>/', download_cv, name='download_cv'),
    path('api/unread-messages/', unread_messages_count, name='unread-messages'),
    path('api/mark-messages-read/', mark_messages_read, name='mark-messages-read'),
    path('api/unread-messages-details/', unread_messages_details, name='unread-messages-details'),
    path('admindashboard/', stats_dashboard, name='stats_dashboard'),
]
