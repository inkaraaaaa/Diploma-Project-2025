from django.shortcuts import render
from .models import JobListing
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobListing, Application
from users.models import UserProfile
from sendreview.models import Company
from .forms import ApplicationForm

from django.db.models import Count

# views.py

from django.utils import timezone

from django.utils import timezone

from django.contrib.auth.decorators import login_required

@login_required(login_url='signin')
def job_list(request):
    title = request.GET.get('title', '')
    job_type = request.GET.get('job_type', '')
    location = request.GET.get('location', '')
    course = request.GET.get('course', '')
    companies_selected = request.GET.getlist('company')

    # Обновляем статусы вакансий
    for job in JobListing.objects.all():
        job.update_status_if_needed()

    # Показываем только open-вакансии
    jobs = JobListing.objects.filter(status='open')

    # Дополнительные фильтры
    if title:
        jobs = jobs.filter(title__icontains=title)
    if job_type:
        jobs = jobs.filter(job_type__icontains=job_type)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if course:
        jobs = jobs.filter(course__icontains=course)
    if companies_selected:
        jobs = jobs.filter(company__name__in=companies_selected)

    companies = JobListing.objects.values('company__name').distinct()

    return render(request, 'draft.html', {
        'jobs': jobs,
        'companies': companies,
        'companies_selected': companies_selected,
    })

# views.py
@login_required(login_url='signin')
def job_list_view(request):
    job_types = request.GET.getlist('type')
    if job_types:
        job_list = JobListing.objects.filter(job_type__in=job_types)
    else:
        job_list = JobListing.objects.all()

    return render(request, 'draft.html', {'job_list': job_list})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    student = request.user

    if Application.objects.filter(student=student, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.job = job
            application.save()
            messages.success(request, 'Application submitted successfully.')
            return redirect('job_detail', job_id=job.id)
    else:
        form = ApplicationForm()

    return render(request, 'company/apply_form.html', {'job': job, 'form': form})

def success_view(request):
    return render(request, 'successent.html')