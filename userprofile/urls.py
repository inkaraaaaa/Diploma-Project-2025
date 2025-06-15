from django.urls import path
from .views import upload_profile_photo, update_about_me, edit_profile, upload_document, view_pdf, get_notifications, get_unread_count
from.views import student_applications_view
from .views import mark_notification_read
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload-profile-photo/', upload_profile_photo, name='upload_profile_photo'),
    path('update-about-me/', update_about_me, name='update_about_me'),
    path('edit/', edit_profile, name='edit_profile'),
    path('upload/', upload_document, name='upload_document'),
    path('document/<int:doc_id>/view/', view_pdf, name='view_pdf'),
    path('get-notifications/', get_notifications, name='get_notifications'),
    path('unread-count/', get_unread_count, name='get_unread_count'),
    path('mark-notification-read/', mark_notification_read, name='mark_notification_read'),
    path('my-applications/', student_applications_view, name='student_applications'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)