import datetime

from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group
from .models import User, DayOfTheWeek, Request, BankTransaction, Student
from django.utils import timezone

class DateInput(forms.DateInput):
    input_type = 'date'


class NewRequestViewForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['availability', 'number_of_lessons', 'interval_between_lessons',
                  'duration_of_lessons', 'further_information']

    availability = forms.ModelMultipleChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Available Days",
        widget=forms.CheckboxSelectMultiple
    )
    def save(self,user): #Pass in user? This is kind of bad. Unsure of a work around for this.
        super().save(commit=False)
        request = Request.objects.create(
            date=timezone.datetime.now(tz=timezone.utc),
            user=user,
            number_of_lessons=self.cleaned_data.get('number_of_lessons'),
            interval_between_lessons=self.cleaned_data.get('interval_between_lessons'),
            duration_of_lessons=self.cleaned_data.get('duration_of_lessons'),
            further_information=self.cleaned_data.get('further_information')
        )
        for available_day in self.cleaned_data.get('availability'):
            request.availability.add(available_day)
            
        return request


class RequestViewForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['date', 'user', 'availability', 'number_of_lessons', 'interval_between_lessons',
                  'duration_of_lessons', 'further_information', 'fulfilled']
        widgets = {'user': forms.HiddenInput()}

    availability = forms.ModelMultipleChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Available Days",
        widget=forms.CheckboxSelectMultiple
    )


class LogInForm(forms.Form):
    email = forms.CharField(label='email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='password must contain an uppercase character, a lower case character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'confirmation does not match password.')

    def save(self):
        super().save(commit=False)  # Do everything the save function would normally do except for storing the record in the database.
        user = User.objects.create_user(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        student_group = Group.objects.get(name='Student')
        student_group.user_set.add(user) # Add user as a Student
        student = Student.objects.create(user=user)
        return student
    #email = forms.EmailField(label='Email')
    #password = forms.CharField(label='Password', widget=forms.PasswordInput())


class TransactionSubmitForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = ['date', 'student', 'amount', 'invoice_number']
        widgets = {
            'date': DateInput()
        }

    # TODO: generate invoice number automatically from student chosen, for now manually submit the invoice number, prone to error.

    def save(self):
        super().save(commit=False)

        BankTransaction.objects.create(
            date=self.cleaned_data.get('date'),
            student=self.cleaned_data.get('student'),
            amount=self.cleaned_data.get('amount'),
            invoice_number=self.cleaned_data.get('invoice_number')
        )

        student=self.cleaned_data.get('student')
        amount=self.cleaned_data.get('amount')
        current_balance = student.balance
        student.balance = current_balance + amount
        student.save()



    def generate_invoice_num(self, student):
        # check student object to see the number of transactions that have been made by the student
        # get student id (primary key) from object
        # alter string so that it fits the form xxxx-yyy
        pass

