from django.urls import path
from .views import upload_profile_photo, update_about_me, edit_profile, upload_document, view_pdf
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload-profile-photo/', upload_profile_photo, name='upload_profile_photo'),
    path('update-about-me/', update_about_me, name='update_about_me'),
    path('edit/', edit_profile, name='edit_profile'),
    path('upload/', upload_document, name='upload_document'),
    path('document/<int:doc_id>/view/', view_pdf, name='view_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)