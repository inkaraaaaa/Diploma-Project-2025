from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import UserProfile
from .models import ContactMessage

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label="Name")
    last_name = forms.CharField(max_length=50, required=True, label="Surname")
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ("username","first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@stu.sdu.edu.kz"):
            raise ValidationError("You must use your university email.")
        return email

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={"class": "form-control"}))


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'message']




class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_photo']



