from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from users.models import UserProfile, ContactMessage
from sendreview.models import Company, Internship
from sendreview.forms import InternshipForm
from .forms import CompanyForm
from vacancies.models import JobListing
from .forms import JobListingForm, CityForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime
from django.db.models import Count
from vacancies.models import Application
import csv
from django.http import HttpResponse
from plotly.offline import plot
import plotly.express as px
from django.db.models.functions import TruncMonth
from django.utils.timezone import now

def staff_required(function=None, login_url='/adminlogin/'):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name='next'
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def custom_logout(request):
    logout(request)
    return redirect('/adminlogin/')

@staff_required
def admin_panel(request):
    context = {
        'company_chart': top_companies_chart(),
        'job_chart': top_jobs_by_applications(),
        'trend_chart': job_posting_trend(),
    }
    return render(request, "admin.html", context)

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Аутентификация пользователя
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Проверка на is_staff
            if user.is_staff:
                login(request, user)
                return redirect('/admin_panel/')  # Перенаправление в админку
            else:
                return render(request, 'adminlogin.html', {'error_message': 'You do not have admin access.'})
        else:
            return render(request, 'adminlogin.html', {'error_message': 'Invalid username or password.'})
    else:
        return render(request, 'adminlogin.html')

@staff_required
def get_dashboard_data(request):
    students_count = UserProfile.objects.count()
    vacancies_count = JobListing.objects.count()
    applications_count = Application.objects.count()

    data = {
        "students": students_count,
        "vacancies": vacancies_count,
        "applications": applications_count,
    }
    return JsonResponse(data)

@staff_required
def students_list(request):
    students = UserProfile.objects.all()
    return render(request, 'students.html', {'students': students})

@staff_required
def company_list(request):
    companies = Company.objects.prefetch_related('cities').all()
    return render(request, 'companies.html', {'companies': companies})

@staff_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_list')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'admin_company_edit.html', {'form': form, 'company': company})

@staff_required
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        return redirect('company_list')
    return render(request, 'admin_company_delete_confirm.html', {'company': company})

@staff_required
def company_add(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('company_list')
        else:
            # Если ошибка - передаем форму обратно с файлами
            return render(request, 'admin_company_add.html', {'form': form})
    else:
        form = CompanyForm()
    return render(request, 'admin_company_add.html', {'form': form})

@staff_required
def job_listing_list(request):
    job_listings = JobListing.objects.select_related('company').all()
    return render(request, 'internships.html', {'job_listings': job_listings})

@staff_required
def job_listing_add(request):
    if request.method == 'POST':
        form = JobListingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_listing_list')
    else:
        form = JobListingForm()
    return render(request, 'admin_job_listing_add.html', {'form': form})

@staff_required
def job_listing_edit(request, job_id):
    job_listing = get_object_or_404(JobListing, pk=job_id)
    if request.method == 'POST':
        form = JobListingForm(request.POST, instance=job_listing)
        if form.is_valid():
            form.save()
            return redirect('job_listing_list')
    else:
        form = JobListingForm(instance=job_listing)
    return render(request, 'admin_job_listing_edit.html', {'form': form, 'job_listing': job_listing})

@staff_required
def job_listing_delete(request, job_id):
    job_listing = get_object_or_404(JobListing, pk=job_id)
    if request.method == 'POST':
        job_listing.delete()
        return redirect('job_listing_list')
    return render(request, 'admin_job_listing_delete_confirm.html', {'job_listing': job_listing})

def unread_messages_count(request):
    count = ContactMessage.objects.filter(is_read=False).count()
    return JsonResponse({'unread_count': count})

@csrf_exempt
def mark_messages_read(request):
    if request.method == "POST":
        ContactMessage.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def unread_messages_details(request):
    messages = ContactMessage.objects.all().order_by("-submitted_at")[:10]
    result = []
    for msg in messages:
        result.append({
            "id": msg.id,
            "first_name": msg.first_name,
            "last_name": msg.last_name,
            "email": msg.email,
            "message": msg.message[:100],
            "time": localtime(msg.submitted_at).strftime("%d-%m-%Y %H:%M"),
            "is_read": msg.is_read,
        })
    return JsonResponse({"messages": result})

@staff_required
def application_list(request):
    job_applications = JobListing.objects.annotate(num_applicants=Count('application'))

    return render(request, 'admin_application_list.html', {
        'job_applications': job_applications
    })

@staff_required
def application_detail(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    applications = Application.objects.filter(job=job).select_related('student')
    return render(request, 'admin_application_detail.html', {
        'job': job,
        'applications': applications
    })

def export_applicants_csv(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    applications = Application.objects.filter(job=job).select_related('student')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="applicants_{job.id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Email', 'Phone', 'Course', 'City'])

    for application in applications:
        student = application.student
        writer.writerow([
            f'{student.first_name} {student.last_name}',
            student.email,
            student.phone_number,
            student.university_course,
            student.city
        ])

    return response

from django.http import HttpResponse, FileResponse, Http404

def download_cv(request, student_id):
    try:
        student = UserProfile.objects.get(id=student_id)
        cv_doc = student.get_cv()  # должен возвращать объект Document

        if not cv_doc or not cv_doc.upload:
            raise Http404("CV not found")

        # Формируем красивое имя файла
        filename = f"CV_{student.first_name}_{student.last_name}.pdf"
        return FileResponse(cv_doc.upload.open(), as_attachment=True, filename=filename)

    except UserProfile.DoesNotExist:
        raise Http404("Student not found")

@csrf_exempt
def delete_message(request, message_id):
    if request.method == "DELETE":
        ContactMessage.objects.filter(id=message_id).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid method'}, status=400)

@staff_required
def internship_list(request):
    internships = Internship.objects.select_related('user', 'company').all()
    return render(request, 'internship_list.html', {'internships': internships})

@staff_required
def internship_add(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('internship_list')
    else:
        form = InternshipForm()
    return render(request, 'internship_form.html', {'form': form, 'title': 'Add Internship'})

@staff_required
def internship_edit(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
            return redirect('internship_list')
    else:
        form = InternshipForm(instance=internship)
    return render(request, 'internship_form.html', {'form': form, 'title': 'Edit Internship'})

@staff_required
def internship_delete(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        internship.delete()
        return redirect('internship_list')
    return render(request, 'internship_confirm_delete.html', {'internship': internship})

@staff_required
def add_city(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_add')  # Название url к форме добавления компании
    else:
        form = CityForm()
    return render(request, 'add_city.html', {'form': form})

def top_companies_chart():
    data = JobListing.objects.values('company__name').annotate(total=Count('id')).order_by('-total')[:5]
    fig = px.bar(
        x=[d['total'] for d in data],
        y=[d['company__name'] for d in data],
        orientation='h',
        labels={'x': 'Vacancies', 'y': 'Company'},
        title='Top-5 Companies Offering the Most Internships',
        color_discrete_sequence=['#8a2be2'] 
    )
    fig.update_layout(width=800, height=500)
    return plot(fig, output_type='div')


def top_jobs_by_applications():
    data = Application.objects.values('job__title').annotate(count=Count('id')).order_by('-count')[:5]
    fig = px.bar(
        x=[d['job__title'] for d in data],
        y=[d['count'] for d in data],
        labels={'x': 'Job Title', 'y': 'Applications'},
        title='Top-5 Most Applied Internships',
    )
    fig.update_layout(
        width=800,
        height=500,
        xaxis_tickangle=45,  # повернули надписи
        xaxis_tickfont=dict(size=10)  # уменьшили шрифт
    )
    return plot(fig, output_type='div')





def job_posting_trend():
    data = (
        JobListing.objects
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    fig = px.line(
        x=[d['month'] for d in data],
        y=[d['count'] for d in data],
        labels={'x': 'Month', 'y': 'New Vacancies'},
        title='Monthly Internship Posting Trends',
    )
    fig.update_layout(width=800, height=500)
    return plot(fig, output_type='div')


def stats_dashboard(request):
    context = {
        'company_chart': top_companies_chart(),
        'job_chart': top_jobs_by_applications(),
        'trend_chart': job_posting_trend(),
    }
    return render(request, 'dashboard.html', context)



