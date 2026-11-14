from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Organization, VolunteerProfile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=[('volunteer', 'Volunteer'), ('coordinator', 'Organization Coordinator')])
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = ('phone', 'bio', 'interests')

class OrganizationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Example: contact@ngo.org'}), help_text='Example: contact@ngo.org')
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'placeholder': 'Example: https://www.ngo.org'}), help_text='Include https://, or leave blank.')
    class Meta:
        model = Organization
        exclude = ('status', 'coordinators', 'approved_by')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Example: Green Earth Foundation'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the organization and its work.'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Example: +91 98765 43210'}),
            'address': forms.TextInput(attrs={'placeholder': 'Example: Noida, Uttar Pradesh'}),
        }
