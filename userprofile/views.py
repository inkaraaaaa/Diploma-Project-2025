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
    document = get_object_or_404(Document, id=doc_id)

    # Открываем файл, который был загружен
    with open(document.upload.path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename={document.title}.pdf'
    return response


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
