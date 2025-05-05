from django import forms
from users.models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'university_course', 'city', 'phone_number', 'birthday', 'cv']
