from django import forms
from .models import DayOfTheWeek, Request

class RequestViewForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['date', 'availability', 'number_of_lessons', 'interval_between_lessons',
                'duration_of_lessons', 'further_information', 'fulfilled']
    
    availability = forms.ModelMultipleChoiceField(
        queryset=DayOfTheWeek.objects.all(), 
        label="Available Days", 
        widget=forms.CheckboxSelectMultiple
    )
