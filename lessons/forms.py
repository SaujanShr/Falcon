from django import forms
from .models import Request

'''
Code for request form here.
Student id should already be set by the browser not the user, not sure how this is implemented.
Availability is a many-to-many relation so a student can select multiple days.
This means the form must have a custom forms.ModelMultipleChoiceField with a queryset of days.
The queryset is already in the Days class when you need to use it.
The rest should be basic.
-Saujan
'''