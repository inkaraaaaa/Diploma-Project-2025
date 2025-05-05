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
from .forms import JobListingForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime
from django.db.models import Count
from vacancies.models import Application
import csv
from django.http import HttpResponse

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
    return render(request, "admin.html")

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

def download_cv(request, user_id):
    user = get_object_or_404(UserProfile, id=user_id)
    document = user.documents.first()
    if not document or not document.upload:
        raise Http404("CV not found")

    file_path = document.upload.path
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        filename = f"{user.first_name}_{user.last_name}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

@csrf_exempt
def delete_message(request, message_id):
    if request.method == "DELETE":
        ContactMessage.objects.filter(id=message_id).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid method'}, status=400)

def internship_list(request):
    internships = Internship.objects.select_related('user', 'company').all()
    return render(request, 'internship_list.html', {'internships': internships})

def internship_add(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('internship_list')
    else:
        form = InternshipForm()
    return render(request, 'internship_form.html', {'form': form, 'title': 'Add Internship'})

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

def internship_delete(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        internship.delete()
        return redirect('internship_list')
    return render(request, 'internship_confirm_delete.html', {'internship': internship})



