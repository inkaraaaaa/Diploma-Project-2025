from django.shortcuts import render
from .models import JobListing
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobListing, Application
from users.models import UserProfile
from sendreview.models import Company

from django.db.models import Count

# views.py

from django.contrib.auth.decorators import login_required

@login_required(login_url='signin')
def job_list(request):
    title = request.GET.get('title', '')
    job_type = request.GET.get('job_type', '')
    location = request.GET.get('location', '')
    course = request.GET.get('course', '')
    companies_selected = request.GET.getlist('company')

    jobs = JobListing.objects.all()

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
    student = request.user  # это уже UserProfile, если ты заменил AUTH_USER_MODEL

    if Application.objects.filter(student=student, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
    else:
        Application.objects.create(student=student, job=job)
        messages.success(request, 'Application submitted successfully.')

    return redirect('job_detail', job_id=job.id)