from django import forms
from vacancies.models import JobListing
class HRFinalRegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'readonly': 'readonly'}))
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")

class InternshipForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ['title', 'description', 'job_type', 'experience_required', 'level', 'start_date', 'deadline', 'location', 'responsibilities', 'requirements']
