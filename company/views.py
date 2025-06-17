from django.shortcuts import render, redirect
from .models import HRCompanyRequest, Interview
from sendreview.models import City
from django.core.mail import send_mail
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import HRCompanyRequest, HRCompany
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login
from .models import HRCompanyRequest, HRCompany
from .forms import HRFinalRegisterForm  
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from users.models import UserProfile, Notification
from sendreview.models import Company, CompanyCity
from django.contrib.auth.decorators import login_required
from .forms import InternshipForm
from vacancies.models import JobListing, Application
import json
from django.http import JsonResponse
from datetime import datetime
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django import forms
from admin_panel.forms import CompanyForm


def hr_required(function=None, login_url='/hr/register/'):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and getattr(u, 'is_hr', False),
        login_url=login_url,
        redirect_field_name='next'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def hr_register_email(request):
    if request.method == 'POST':
        hr_email = request.POST['hr_email']
        return redirect(f'/hr/register/info/?email={hr_email}')
    return render(request, 'hr_register_email.html')

def hr_register_info(request):
    hr_email = request.GET.get('email') or request.POST.get('hr_email')
    if request.method == 'POST':
        HRCompanyRequest.objects.create(
            company_name=request.POST['company_name'],
            logo=request.FILES.get('logo'),
            overview=request.POST['overview'],
            partnership=request.POST['partnership'],
            city_id=request.POST['city'],
            employee_count=request.POST['employee_count'],
            hr_name=request.POST['hr_name'],
            hr_email=hr_email,
            token=uuid.uuid4().hex
        )
        return redirect('hr_register_complete')
    
    cities = City.objects.all()
    return render(request, 'hr_register_info.html', {'hr_email': hr_email, 'cities': cities})

def hr_register_complete(request):
    return render(request, 'hr_register_complete.html')

def hr_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # обычно email
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'hrcompany'):
            login(request, user)
            return redirect('hr_vacancies')  # имя URL'а на панель HR
        else:
            messages.error(request, 'Неверные данные или вы не HR.')

    return render(request, 'hr_login.html')

def hr_requests_list(request):
    requests = HRCompanyRequest.objects.all().order_by('-submitted_at')
    return render(request, 'hr_requests_list.html', {'requests': requests})

def hr_request_detail(request, pk):
    req = get_object_or_404(HRCompanyRequest, pk=pk)
    return render(request, 'hr_request_detail.html', {'request_obj': req})

def approve_hr_request(request, pk):
    req = get_object_or_404(HRCompanyRequest, pk=pk)
    if req.is_reviewed:
        return redirect('hr_requests_list')

    req.is_reviewed = True
    req.is_approved = True
    req.save()

    # Отправляем письмо HR с ссылкой на регистрацию
    registration_link = f"{request.scheme}://{request.get_host()}/hr/final-register/?token={req.token}"
    send_mail(
        'Your HR Company Request is Approved',
        f"Your request has been approved. Please complete registration: {registration_link}",
        settings.DEFAULT_FROM_EMAIL,
        [req.hr_email],
    )

    return redirect('hr_requests_list')

def reject_hr_request(request, pk):
    req = get_object_or_404(HRCompanyRequest, pk=pk)
    if req.is_reviewed:
        return redirect('hr_requests_list')

    req.is_reviewed = True
    req.is_approved = False
    req.save()

    # Уведомление об отказе
    send_mail(
        'Your HR Company Request was Rejected',
        'Unfortunately, your HR company registration request was rejected.',
        settings.DEFAULT_FROM_EMAIL,
        [req.hr_email],
    )

    return redirect('hr_requests_list')

def hr_register_user(request):
    token = request.GET.get('token')
    request_obj = HRCompanyRequest.objects.filter(token=token, is_approved=True).first()

    if not request_obj:
        return HttpResponse("Неверный токен или заявка не одобрена.", status=400)

    if request.method == 'POST':
        form = HRFinalRegisterForm(request.POST)
        if form.is_valid():
            user = UserProfile.objects.create_user(
                username=request_obj.hr_email,
                email=request_obj.hr_email,
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                is_hr=True
            )
            login(request, user)
            request.session['hr_user_id'] = user.id  # сохраним временно
            request.session['request_token'] = token
            return redirect('hr_register_company')
    else:
        form = HRFinalRegisterForm(initial={'email': request_obj.hr_email})

    return render(request, 'hr_register_user.html', {'form': form, 'request_obj': request_obj})

@login_required
def hr_register_company(request):
    user_id = request.session.get('hr_user_id')
    token = request.session.get('request_token')
    request_obj = HRCompanyRequest.objects.filter(token=token, is_approved=True).first()

    if not request_obj:
        return HttpResponse("Ошибка токена", status=400)

    if request.method == 'POST':
        hr_user = request.user

    company = Company.objects.create(
    name=request_obj.company_name,
    logo=request_obj.logo,
    overview=request_obj.overview,
    partnership=request_obj.partnership
    )

    hr_company = HRCompany.objects.create(
    name=request_obj.company_name,
    logo=request_obj.logo,
    overview=request_obj.overview,
    employee_count=request_obj.employee_count,
    partnership=request_obj.partnership,
    city=request_obj.city,
    user=hr_user,
    company=company  # 👈 теперь company_id будет не NULL
    )

    CompanyCity.objects.create(company=company, city=request_obj.city)
    return redirect('hr_dashboard')
    return render(request, 'hr_register_company.html', {'request_obj': request_obj})

@hr_required
def hr_dashboard(request):
    return render(request, 'hr_dashboard.html')







@hr_required
def delete_internship(request, pk):
    internship = get_object_or_404(JobListing, pk=pk, company=request.user.hrcompany.company)

    if request.method == 'POST':
        internship.delete()
        return redirect('internship_list')

    return render(request, 'hr_delete_internship_confirm.html', {'internship': internship})

@hr_required
def application_detail(request, pk):
    internship = get_object_or_404(JobListing, pk=pk)
    applications = Application.objects.filter(job=internship).select_related('student')

    return render(request, 'hr_applicant_list.html', {
        'internship': internship,
        'applications': applications,
    })

@hr_required
def download_cv(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)

    if not user.cv:
        raise Http404("CV not found")

    response = HttpResponse(user.cv, content_type='application/pdf')
    filename = f"{user.first_name}_{user.last_name}_CV.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@hr_required
def applicant_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    return render(request, 'hr_applicant_detail.html', {'application': application})

@hr_required
@csrf_exempt
def save_interview(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        app_id = data.get('app_id')
        date = data.get('date')
        time = data.get('time')
        format = data.get('format')
        location = data.get('location')
        phone = data.get('phone')

        try:
            application = Application.objects.get(id=app_id)

            # Создаём интервью
            Interview.objects.create(
                application=application,
                date=date,
                time=time,
                format=format,
                location=location,
                phone=phone
            )

            # Обновляем статус заявки
            application.invited_to_interview = True
            application.save()

            # ✅ Уведомление студенту
            Notification.objects.create(
                recipient=application.student,
                message=(
                    f'Company "{application.job.company.name}" invites you to the position "{application.job.title}". '
                    f'Interview details: {date} at {time}, Format: {format.capitalize()}, '
                    f'Location: {location}, Phone: {phone}.'
                )
            )

            return JsonResponse({'status': 'success'})
        except Application.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Application not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
@require_POST
def reject_application(request):
    data = json.loads(request.body)
    app_id = data.get('app_id')

    try:
        # Используем правильное имя поля: 'job' вместо 'internship'
        application = Application.objects.select_related('job__hr_company').get(id=app_id)

        # Проверка, принадлежит ли вакансия текущему HR
        if application.job.hr_company.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

        application.rejected = True
        application.save()

        # Уведомление студенту
        Notification.objects.create(
            recipient=application.student,
            message=f"Thank you for your interest in the position '{application.job.title}' at '{application.job.hr_company.name}'. Unfortunately, your application was not successful this time."
        )

        return JsonResponse({'status': 'success'})

    except Application.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Application not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def hr_vacancies_view(request):
    hr_company = get_object_or_404(HRCompany, user=request.user)
    internships = JobListing.objects.filter(hr_company=hr_company).order_by('-created_at')
    form = InternshipForm()
    
    # Форма для каждого объекта
    edit_forms = {intern.id: InternshipForm(instance=intern) for intern in internships}

    return render(request, 'hr_vacancies.html', {
        'internships': internships,
        'form': form,
        'edit_forms': edit_forms
    })
    
@login_required
def hr_add_internship(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            internship = form.save(commit=False)
            internship.hr_company = HRCompany.objects.get(user=request.user)
            internship.company = internship.hr_company.company  # привязка к company
            internship.save()
    return redirect('hr_vacancies')


@login_required
def hr_edit_internship(request, internship_id):
    internship = get_object_or_404(JobListing, id=internship_id, hr_company__user=request.user)

    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
    return redirect('hr_vacancies')


@login_required
def hr_delete_internship(request, internship_id):
    internship = get_object_or_404(JobListing, id=internship_id, hr_company__user=request.user)
    internship.delete()
    return redirect('hr_vacancies')

def application_detail(request, pk):
    internship = get_object_or_404(JobListing, pk=pk)
    applications = Application.objects.filter(job=internship).select_related('student')

    context = {
        'internship': internship,
        'applications': applications,
    }
    return render(request, 'hr_vacancy_detail.html', context)

@require_POST
def accept_application(request):
    import json
    data = json.loads(request.body)

    app_id = data.get('app_id')
    comment = data.get('comment')

    try:
        application = Application.objects.get(id=app_id)
        application.accepted = True
        application.rejected = False
        application.save()

        # Создать уведомление студенту
        Notification.objects.create(
            recipient=application.student,
            message=f"🎉 Congratulations! You have been accepted to the interview. HR comment: {comment}"
        )

        return JsonResponse({'status': 'success'})
    except Application.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Application not found'})
    
@login_required
def hr_profile_view(request):
    hr_company = get_object_or_404(HRCompany, user=request.user)
    company = hr_company.company
    form = CompanyForm(instance=company)

    return render(request, 'hr_profile.html', {
    'hr_company': hr_company,
    'hr_user': request.user,
    'company': company,
    'form': form,
})



from django.views.decorators.http import require_POST

from django.http import HttpResponseNotAllowed

@login_required
def edit_company(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    hr_company = get_object_or_404(HRCompany, user=request.user)
    company = hr_company.company

    form = CompanyForm(request.POST, request.FILES, instance=company)
    if form.is_valid():
        form.save()
        return HttpResponse("OK")
    return HttpResponse("Form invalid", status=400)

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse

@login_required
def hr_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # чтобы не разлогинило
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_text()})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

from django.contrib.auth import logout

def custom_logout(request):
    logout(request)
    return redirect('hr/login/')

from vacancies.models import JobListing
from django.contrib.auth.decorators import login_required

@login_required
def delete_internship(request, pk):
    internship = get_object_or_404(JobListing, id=pk, company=request.user.hrcompany.company)

    if request.method == 'POST':
        internship.delete()
        return redirect('hr_vacancies')  # замени на свою главную страницу

    # если метод GET — вернём ошибку (или можно сделать модалку подтверждения)
    return redirect('hr_vacancies')