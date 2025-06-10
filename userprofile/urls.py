from django.urls import path
from .views import upload_profile_photo, update_about_me, edit_profile, view_pdf, delete_profile, profile_view, change_password, edit_social_networks
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('user/<str:username>/', profile_view, name='user_profile'),
    path('upload-profile-photo/', upload_profile_photo, name='upload_profile_photo'),
    path('update-about-me/', update_about_me, name='update_about_me'),
    path('edit/', edit_profile, name='edit_profile'),
    path('document/<int:doc_id>/view/', view_pdf, name='view_pdf'),
    path('delete-profile/', delete_profile, name='delete_profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('change-password/', change_password, name='change_password'),
    path('edit-social-networks/', edit_social_networks, name='edit_social_networks')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)