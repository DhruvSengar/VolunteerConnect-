from django import forms
from .models import HourLog, Opportunity, Review

class OpportunityForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), help_text='Example: 2026-12-15')
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), help_text='Example: 09:00 AM')
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), help_text='Example: 01:00 PM')
    class Meta:
        model = Opportunity
        exclude = ('organization', 'created_at')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Example: Beach cleanup drive'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe the activity and its impact.'}),
            'location': forms.TextInput(attrs={'placeholder': 'Example: Sector 18, Noida'}),
            'capacity': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Example: 25'}),
            'requirements': forms.Textarea(attrs={'placeholder': 'Example: Comfortable shoes and water bottle'}),
        }

class HourLogForm(forms.ModelForm):
    class Meta:
        model = HourLog
        fields = ('hours', 'notes')
    def clean_hours(self):
        value = self.cleaned_data['hours']
        if value <= 0: raise forms.ValidationError('Hours must be greater than zero.')
        return value

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
    def clean_rating(self):
        value = self.cleaned_data['rating']
        if not 1 <= value <= 5: raise forms.ValidationError('Rating must be from 1 to 5.')
        return value
