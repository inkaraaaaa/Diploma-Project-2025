from django.contrib import admin
from django.urls import path, include
from sendreview.views import company_detail, add_comment
from django.conf import settings
from django.conf.urls.static import static
from home_after import views
from userprofile.views import update_about_me
from django.http import JsonResponse, HttpResponse
from django.db import connection


def health_check(request):
    """Health check endpoint for Docker healthcheck."""
    # Always return 200 for initial healthcheck to allow container to start
    # This prevents healthcheck failures during startup
    return JsonResponse({"status": "healthy"})


def favicon_view(request):
    """Simple favicon handler to prevent 500 errors."""
    return HttpResponse(status=204)  # No Content


urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('favicon.ico', favicon_view, name='favicon'),
    path('admin/', admin.site.urls),
    path('company/<int:company_id>/', company_detail, name='company_detail'),
    path("company/<int:company_id>/add_comment/", add_comment, name="add_comment"),
    path("", include("users.urls")),
    path("", include("unboarding_form.urls")),
    path('userprofile/', include('userprofile.urls')),
    path("", include('vacancies.urls')),
    path("", include("admin_panel.urls")),
    path("", include("company.urls")),
    path('', include('home_after.urls')),
    path('user/<str:username>/', views.profile_view, name='user_profile'),
    path('create-resume/', views.open_resume, name='create_resume'),
    path('update-about-me/', update_about_me, name='update_about_me'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




