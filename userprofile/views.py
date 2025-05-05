from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import UserProfileForm
from .forms import DocumentForm
from .models import Document
from django.shortcuts import get_object_or_404
from django.http import HttpResponse



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
    success_message = ''
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Сохраняем документ в БД
            success_message = 'Document successfully uploaded!'
            # Перенаправляем на страницу профиля с параметром успешной загрузки
            return redirect(f'/user/{request.user.username}/')  # Перенаправление на профиль пользователя
    else:
        form = DocumentForm()

    return render(request, 'upload-document.html', {'form': form, 'success_message': success_message})

def view_pdf(request, doc_id):
    # Получаем документ или возвращаем 404, если не найден
    document = get_object_or_404(Document, id=doc_id)

    # Открываем файл, который был загружен
    with open(document.upload.path, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename={document.title}.pdf'  # Открывается в браузере
    return response