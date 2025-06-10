from django.contrib.auth.views import LogoutView
from .views import signup
from .views import success_signup
from .views import success_signin
from .views import logout_view
from .views import home_before_login
from .views import main_page
from .views import faq, contact_view, contact_success_view
from django.contrib.auth import views as auth_views
from .views import (
    password_reset_request,
    password_reset_confirm,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)
from django.urls import path, include
from .views import  (verify_code, vacancies)


urlpatterns = [
    path("signup/", signup, name="signup"),
    path("verify/", verify_code, name="verify"),
    path("success_signup/", success_signup, name="success-signup"),
    path("signin/", auth_views.LoginView.as_view(template_name="signin.html"), name="signin"),
    path("success-signin/", success_signin, name="success_signin"),
    path('logout/', LogoutView.as_view(next_page='main_page'), name='logout'),
    path('', main_page, name="main_page"),
    path('faq/', contact_view, name="faq"),
    path('contact-success/', contact_success_view, name='contact_success'),
    path('logout/', logout_view, name='logout'),
    path('', home_before_login, name='home-be'),
    path('home-be/', home_before_login),
    path('', main_page),
    path("password_reset/", password_reset_request, name="password_reset"),
    path("reset/<uidb64>/<token>/", password_reset_confirm, name="password_reset_confirm"),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password_reset/complete/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]