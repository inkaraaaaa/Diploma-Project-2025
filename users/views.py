from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import SignUpForm, PasswordResetRequestForm
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.views.generic import TemplateView

from .forms import ContactForm

from django.shortcuts import redirect, render
from vacancies.models import JobListing
from sendreview.models import Comment
from users.models import UserProfile


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            send_verification_code(request, email)  # Отправка кода

            # Сохраняем введенные данные в сессии
            request.session["signup_data"] = request.POST

            return redirect("verify")  # Перенаправляем на страницу ввода кода

    else:
        form = SignUpForm()

    return render(request, "signup.html", {"form": form})

def verify_code(request):
    email = request.session.get("verification_email")
    stored_code = request.session.get("verification_code")

    if not email:
        return redirect("signup")  # Если email не найден, возвращаемся к регистрации

    if request.method == "POST":
        entered_code = request.POST.get("verification_code", "").strip()

        if entered_code == stored_code:
            form_data = request.session.get("signup_data")
            form = SignUpForm(form_data)

            if form.is_valid():
                user = form.save()
                login(request, user)

                # Удаляем использованный код и данные из сессии
                request.session.pop("verification_code", None)
                request.session.pop("verification_email", None)
                request.session.pop("signup_data", None)

                return redirect("unboarding_form")  # Перенаправляем на анбординг-форму
            else:
                return render(request, "verificationcode.html", {"error": "Form data is invalid."})

        else:
            return render(request, "verificationcode.html", {"error": "Invalid verification code."})

    return render(request, "verificationcode.html")

def success_signup(request):
    return render(request, "sucsignup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
        user = authenticate(request, username=username, password=password)  # Проверяем

        if user is not None:
            login(request, user)  # Логиним
            return redirect("home-after")  # Перенаправляем
        else:
            messages.error(request, "Invalid Student ID or password")  # Сообщение об ошибке

    return render(request, "signin.html")

verification_codes = {}

def send_verification_code(request, email):
    code = str(random.randint(100000, 999999))  # Генерация 6-значного кода

    # Сохраняем код в сессии
    request.session["verification_code"] = code
    request.session["verification_email"] = email

    # Отправляем email
    send_mail(
        "Your Verification Code",
        f"Your verification code is: {code}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def success_signin(request):
    return render(request, "home-after.html")

def home_view(request):
    return render(request, 'home-be.html')

def logout_view(request):
    logout(request)
    comments = Comment.objects.all()
    return render(request, 'home-be.html', {'comments': comments})

def main_page(request):
    comments = Comment.objects.all()
    return render(request, 'home-be.html', {'comments': comments})

def vacancies(request):
    comments = Comment.objects.all()
    return render(request, 'home-be.html', {'comments': comments})


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = UserProfile.objects.filter(email=email).first()  # Используем UserProfile
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
                )
                message = render_to_string("email_template.html", {"reset_link": reset_link, "username": user.username})
                send_mail(
                    "Reset Your Password",
                    "Click the link below to reset your password:\n" + reset_link,
                    "noreply@yourdomain.com",
                    [email],
                    fail_silently=False,
                    html_message=message,
                )
                return redirect("password_reset_done")
    else:
        form = PasswordResetRequestForm()
    return render(request, "repass.html", {"form": form})

def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserProfile.objects.get(pk=uid)  # если у тебя кастомная модель
    except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                print("Форма валидна!")  # 👉 Проверим, проходит ли форма
                form.save()
                update_session_auth_hash(request, user)
                return redirect("password_reset_complete")
            else:
                print("Ошибки формы:", form.errors)  # 👉 Выведем ошибки формы

        else:
            form = SetPasswordForm(user)
        return render(request, "createpass.html", {"form": form})
    
    return render(request, "password_reset_invalid.html")

class PasswordResetDoneView(TemplateView):
    template_name = "password_reset_done.html"

class PasswordResetCompleteView(TemplateView):
    template_name = "password_reset_complete.html"

def afisha(request):
    return render(request, "home-after.html")


def faq(request):
    return render(request, "faq.html")

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_success')
    else:
        form = ContactForm()
    return render(request, 'faq.html', {'form': form})

def contact_success_view(request):
    return render(request, 'successent.html')



def home_before_login(request):
    comments = Comment.objects.all()
    return render(request, 'home-be.html', {'comments': comments})


