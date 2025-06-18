from django import forms
from .models import Internship

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        fields = ['user', 'company', 'position', 'start_date', 'end_date']
