from django import forms
from users.models import UserProfile, Language, Skill
from .models import Document


class UserProfileForm(forms.ModelForm):
    languages_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Kazakh, Russian, English'}),
        help_text="Separate languages with commas"
    )
    skills_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Figma, Adobe XD, Prototyping'}),
        help_text="Separate skills with commas"
    )

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'position', 'profile_photo', 'languages_input', 'skills_input']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['languages_input'].initial = ', '.join(self.instance.get_languages_list())
            self.fields['skills_input'].initial = ', '.join(self.instance.get_skills_list())

    def save(self, commit=True):
        user_profile = super().save(commit=False)

        if commit:
            user_profile.save()

            # Process languages
            languages = [lang.strip() for lang in self.cleaned_data['languages_input'].split(',') if lang.strip()]
            user_profile.languages.clear()
            for lang_name in languages:
                lang, _ = Language.objects.get_or_create(name=lang_name)
                user_profile.languages.add(lang)

            # Process skills
            skills = [skill.strip() for skill in self.cleaned_data['skills_input'].split(',') if skill.strip()]
            user_profile.skills.clear()
            for skill_name in skills:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                user_profile.skills.add(skill)

            self.save_m2m()

        return user_profile

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'upload']



class SocialLinksForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['facebook', 'instagram', 'linkedin', 'twitter']