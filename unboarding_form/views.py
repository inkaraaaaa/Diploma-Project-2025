from django.shortcuts import render, redirect
from django.http import HttpResponse
from users.models import UserProfile, Language, Skill

def unboarding_form_view(request):
    return render(request, 'unboarding_form.html')

def unboarding_form_submit(request):
    if request.method == 'POST':
        request.session['username'] = request.POST.get('username')
        request.session['birthday'] = request.POST.get('birthday')
        request.session['university_course'] = request.POST.get('university_course')
        request.session['city'] = request.POST.get('city')
        request.session['phone_number'] = request.POST.get('phone_number')
        
        return redirect('unboarding_form_step2')
    return render(request, 'unboarding_form.html')


def unboarding_form_step2(request):
    return render(request, 'unboarding_form_step2.html')

def unboarding_form_submit_step2(request):
    if request.method == 'POST':
        try:
            # Get form data
            position = request.POST.get('position', '')
            cv_file = request.FILES.get('cv', None)
            languages_input = request.POST.get('languages', '')
            skills_input = request.POST.get('skills', '')

            # Process comma-separated values
            language_names = [name.strip() for name in languages_input.split(',') if name.strip()]
            skill_names = [name.strip() for name in skills_input.split(',') if name.strip()]

            # Handle file upload
            cv_content = None
            if cv_file:
                cv_content = cv_file.read()

            # Get user from session
            username = request.session.get('username')
            if not username:
                return HttpResponse("Username not found in session", status=400)

            # Get or create profile
            user_profile = UserProfile.objects.get_or_create(username=username)[0]

            # Update profile fields
            user_profile.position = position
            if cv_content:
                user_profile.cv = cv_content
            user_profile.save()

            # Add languages
            for lang_name in language_names:
                lang = Language.objects.get_or_create(name=lang_name)[0]
                user_profile.languages.add(lang)

            # Add skills
            for skill_name in skill_names:
                skill = Skill.objects.get_or_create(name=skill_name)[0]
                user_profile.skills.add(skill)

            request.session.flush()
            return redirect('signin')

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return render(request, 'signin.html')

def home_after(request):
    return render(request, 'home-after.html')


# Просмотр профиля
def profile_view(request, username):
    try:
        user_profile = UserProfile.objects.get(username=username)
        return render(request, 'profile.html', {'user_profile': user_profile})
    except UserProfile.DoesNotExist:
        return redirect('unboarding_form')

# Авторизация
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = UserProfile.objects.filter(email=email).first()
        if user:
            request.session['username'] = user.username
            return redirect('profile_view', username=user.username)
        else:
            return redirect('unboarding_form')
    return render(request, 'signin')

# Загрузка резюме
def download_cv(request, username):
    try:
        user_profile = UserProfile.objects.get(username=username)
        if user_profile.cv:
            response = HttpResponse(user_profile.cv, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="cv.pdf"'
            return response
    except UserProfile.DoesNotExist:
        pass
    return HttpResponse("CV не найден.", status=404)