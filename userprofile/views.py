from asyncio.log import logger
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import os
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
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

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SocialLinksForm




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
    # Получаем пользователя по username или 404
    user = get_object_or_404(User, username=username)

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Удаляем все старые документы пользователя и физические файлы
            old_documents = Document.objects.filter(user=user)
            for doc in old_documents:
                # Удаляем файл с диска, если он существует
                if doc.upload and os.path.isfile(doc.upload.path):
                    try:
                        os.remove(doc.upload.path)
                    except Exception as e:
                        print(f"Ошибка при удалении файла: {e}")
                # Удаляем запись из базы
                doc.delete()

            # Создаем новый документ, привязываем к пользователю и сохраняем
            document = form.save(commit=False)
            document.user = user
            document.save()

            # Перенаправляем обратно на профиль пользователя после загрузки
            return redirect('profile_view', username=user.username)

    else:
        form = DocumentForm()

    # Получаем последний документ пользователя, если есть (после удаления остальных должен быть только 1)
    last_document = Document.objects.filter(user=user).order_by('-id').first()
    documents = [last_document] if last_document else []

    # Отправляем в шаблон форму, пользователя и список с одним документом (или пустой список)
    return render(request, 'userprofile.html', {
        'form': form,
        'user': user,
        'documents': documents,
    })



@login_required
def update_about_me(request):
    if request.method == 'POST':
        user = request.user

        user.position = request.POST.get('position')
        course_value = request.POST.get('university_course')
        user.city = request.POST.get('city')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')

        # Проверка: если значение есть и оно число — сохраняем, иначе ставим None
        if course_value and course_value.isdigit():
            user.university_course = int(course_value)
        else:
            user.university_course = None  # Убедись, что в модели стоит null=True, blank=True

        user.save()
        return redirect('user_profile', username=user.username)
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
            print("Document before save:", document, document.upload, request.user)
            document.user = request.user
            document.save()
            messages.success(request, 'Document successfully uploaded!')
            return redirect(f'/user/{request.user.username}/')
    else:
        form = DocumentForm()

    return render(request, 'upload-document.html', {'form': form})




def view_pdf(request, doc_id):
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
    user_profile = request.user
    notifications = Notification.objects.filter(recipient=user_profile)


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
    response['Content-Disposition'] = f'inline; filename={document.title}.pdf'
    return response


    #response['Content-Disposition'] = f'inline; filename={document.title}.pdf'
    #return response


@login_required
def delete_profile(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home-be')


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user
        if not user.check_password(current_password):
            messages.error(request, 'Текущий пароль введён неверно.')
        elif new_password != confirm_password:
            messages.error(request, 'Новые пароли не совпадают.')
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменён.')
            return redirect('user_profile', username=user.username)

    return render(request, 'change_password.html')

@login_required
def edit_social_networks(request):
    user_profile = request.user  # вот так берём профиль текущего пользователя

    if request.method == 'POST':
        form = SocialLinksForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile', username=request.user.username)

    else:
        form = SocialLinksForm(instance=user_profile)

    return render(request, 'userprofile.html', {'form': form})
