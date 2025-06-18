from django import forms
from sendreview.models import Company, City
from vacancies.models import JobListing

class CompanyForm(forms.ModelForm):
    cities = forms.ModelMultipleChoiceField(
    queryset=City.objects.all(),
    widget=forms.CheckboxSelectMultiple,  # или forms.SelectMultiple
    required=True
    )

    class Meta:
        model = Company
        fields = ['name', 'logo', 'cities', 'overview', 'partnership']

class JobListingForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    deadline = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    status = forms.ChoiceField(
        choices=JobListing.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = JobListing
        fields = [
            'title', 'description', 'job_type', 'experience_required', 'level',
            'company', 'location', 'course', 'about_role',
            'responsibilities', 'requirements', 'start_date', 'deadline', 'status'
        ]

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter city name'}),
        }
