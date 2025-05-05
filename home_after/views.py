from vacancies.models import JobListing
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from sendreview.models import Comment
from .models import Event
from django.contrib.auth.decorators import login_required
from userprofile.models import Document
from userprofile.forms import DocumentForm
from django.shortcuts import redirect



User = get_user_model()

def job_detail(request, job_id):
    job = get_object_or_404(JobListing, id=job_id)
    return render(request, 'jobdetails.html', {'job': job})


def job_list(request):
    title = request.GET.get('title', '')
    job_type = request.GET.get('job_type', '')
    location = request.GET.get('location', '')

    # Filter jobs based on the form input values
    jobs = JobListing.objects.all()

    if title:
        jobs = jobs.filter(title__icontains=title)  # Search by title

    if job_type:
        jobs = jobs.filter(job_type__icontains=job_type)  # Filter by job type

    if location:
        jobs = jobs.filter(location__icontains=location)  # Filter by location

    comments = Comment.objects.all()
    events = Event.objects.all()

    return render(request, 'home-after.html', {'jobs': jobs, 'comments': comments, 'events': events})


def vacancies_view(request):
    jobs = JobListing.objects.all()  # Query all job listings
    return render(request, 'draft.html', {'jobs': jobs})

def after_view(request):
    return render(request, 'home-after.html')



User = get_user_model()

@login_required
def profile_view(request, username):
    # Получаем пользователя по имени (username)
    user = get_object_or_404(User, username=username)

    # Получаем все документы этого пользователя
    documents = Document.objects.filter(user=user)

    # Обработка загрузки документа
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем документ в БД и связываем его с пользователем
            document = form.save(commit=False)
            document.user = user
            document.save()
            success_message = 'Document successfully uploaded!'
            user = get_object_or_404(User, username=username)
            return redirect(f'/user/{user.username}/')  # Перенаправление на профиль пользователя с параметром успешной загрузки
    else:
        form = DocumentForm()

    return render(request, 'userprofile.html', {
        'user': user,
        'form': form,
        'documents': documents,  # Передаем список документов пользователя
        'success_message': success_message if 'success_message' in locals() else '',  # Убедитесь, что переменная существует
    })


def open_resume(request):
    return render(request, 'create_resume.html')


def featured_events(request):
    events = Event.objects.all()
    return render(request, 'home_after.html', {'events': events})


def afisha2_view(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'afisha2.html', {'event': event})
