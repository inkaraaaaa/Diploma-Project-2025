from django.urls import path
from unboarding_form import views as unboarding_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('unboarding_form/', unboarding_views.unboarding_form_view, name='unboarding_form'),
    path('unboarding_form/submit/', unboarding_views.unboarding_form_submit, name='unboarding_form_submit'),
    path('unboarding_form/step2/', unboarding_views.unboarding_form_step2, name='unboarding_form_step2'),
    path('unboarding_form/submit_step2/', unboarding_views.unboarding_form_submit_step2, name='unboarding_form_submit_step2'),
    path('unboarding_form/download_cv/', unboarding_views.download_cv, name='download_cv'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)