from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Optional cover letter...'}),
        required=False,
        label=''
    )

    class Meta:
        model = Application
        fields = ['cover_letter']

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['cover_letter'].required = False
