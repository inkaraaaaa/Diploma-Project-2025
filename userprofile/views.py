from asyncio.log import logger
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import UserProfileForm
from .forms import DocumentForm
from .models import Document
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from users.models import Notification, UserProfile
import logging
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.utils.timezone import is_aware, make_aware
from django.views.decorators.http import require_POST
from vacancies.models import Application
from django.db.models import Prefetch
from company.models import Interview


@csrf_exempt
def upload_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        user = request.user
        user.profile_photo = request.FILES['photo']
        user.save()

        return JsonResponse({
            'status': 'success',
            'photo_url': user.profile_photo.url  # Важно вернуть полный URL
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

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
            return redirect(f'/user/{user.username}/')  # Перенаправление на профиль пользователя с параметром успешной загрузки
    else:
        form = DocumentForm()

    return render(request, 'userprofile.html', {
        'user': user,
        'form': form,
        'documents': documents,  # Передаем список документов пользователя
        'success_message': success_message if 'success_message' in locals() else '',  # Убедитесь, что переменная существует
    })

@login_required
def update_about_me(request):
    if request.method == 'POST':
        user = request.user
        user.position = request.POST.get('position')
        user.university_course = request.POST.get('university_course')
        user.city = request.POST.get('city')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.save()
        return redirect('user_profile', username=request.user.username)



@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.birthday = request.POST.get('birthday')
        user.city = request.POST.get('city')
        user.phone_number = request.POST.get('phone_number')
        user.email = request.POST.get('email')
        user.save()
        return redirect('user_profile', username=user.username)
    return render(request, 'edit_profile.html', {'user': user})

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document successfully uploaded!')
            return redirect(f'/user/{request.user.username}/')
    else:
        form = DocumentForm()

    return render(request, 'upload-document.html', {'form': form})


def view_pdf(request, doc_id):
    # Получаем документ или возвращаем 404, если не найден
    document = get_object_or_404(Document, id=doc_id)

    # Открываем файл, который был загружен
    with open(document.upload.path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename={document.title}.pdf'  # Открывается в браузере
    return response

@login_required
def get_notifications(request):
    now = timezone.now()

    # Удалить уведомления с прошедшими интервью
    past_notifications = Notification.objects.filter(
        interview__isnull=False
    ).select_related('interview')

    for n in past_notifications:
        interview_datetime = datetime.combine(n.interview.date, n.interview.time)
        if timezone.is_naive(interview_datetime):
            interview_datetime = timezone.make_aware(interview_datetime, timezone.get_current_timezone())
        if interview_datetime <= now:
            n.delete()

    # Получить оставшиеся уведомления
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    data = [
        {
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for n in notifications
    ]

    return JsonResponse(data, safe=False)

@login_required
def get_unread_count(request):
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})

@csrf_exempt
@require_POST
@login_required
def mark_notification_read(request):
    try:
        data = json.loads(request.body)
        notification_id = data.get('id')

        # request.user — это UserProfile, всё хорошо
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
    
#@login_required
#def student_applications_view(request):
#    user = request.user  # уже UserProfile
#   applications = Application.objects.filter(student=user).select_related('job__company')

#   context = {
#        'applications': applications
#    }
#    return render(request, 'student_applications.html', context)

@login_required
def student_applications_view(request):
    applications = Application.objects.filter(student=request.user).order_by('-applied_at').prefetch_related(
        Prefetch('interview_set', queryset=Interview.objects.all())
    )
    return render(request, 'student_applications.html', {'applications': applications})





