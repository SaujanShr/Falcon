import datetime

from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group
from .models import User, DayOfTheWeek, Request, BankTransaction, Student, Booking, Invoice
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

    def __init__(self, *args, **kwargs):
        super(RequestViewForm, self).__init__(*args, **kwargs)
        self.fields['date'].disabled = True
        self.fields['fulfilled'].disabled = True

    def setReadOnly(self):
        self.fields['availability'].disabled = True
        self.fields['number_of_lessons'].disabled = True
        self.fields['interval_between_lessons'].disabled = True
        self.fields['duration_of_lessons'].disabled = True
        self.fields['further_information'].disabled = True


class FulfilRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'reqe' in kwargs:
            reqe = kwargs.pop('reqe')
        super(FulfilRequestForm, self).__init__(*args, **kwargs)
        if 'reqe' in locals() and isinstance(reqe, Request):
            self.fields['availability'] = forms.ModelChoiceField(
                queryset=reqe.availability.all(),
                label="Day of lessons:",
                widget=forms.Select
            )
    class Meta:
        model = Booking
        fields = ['availability', 'number_of_lessons', 'interval_between_lessons',
                  'duration_of_lessons', 'further_information']

    date = forms.CharField(
        widget=forms.HiddenInput
    )

    availability = forms.ModelChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Day of lessons:",
        widget=forms.Select
    )

    time_of_lesson = forms.TimeField(
        label='Lesson time:',
        widget=forms.TimeInput(
            attrs={'type':'time'}
        )
    )
    teacher = forms.CharField(
        label='Teacher:',
        widget=forms.TextInput
    )
    start_date = forms.DateField(
        label='Start date:',
        widget=forms.DateInput(
            attrs={'type':'date'}
        )
    )
    hourly_cost = forms.CharField(
        widget=forms.TextInput(
            attrs={'type':'number'}
        )
    )

    """
    def clean(self):
        super().clean()
        req = Request.objects.get(date=self.cleaned_data.get('date'))
        lesson_day = DayOfTheWeek.objects.get(order=(int(self.cleaned_data.get('availability'))-1))
        if lesson_day not in req.availability.all():
            self.add_error('availability', 'Student not available on that day.')
    """

    def save(self):
        super().save(commit=False)
        req = Request.objects.get(date=self.cleaned_data.get('date'))
        if not req.fulfilled:
            booking = Booking.objects.create(
                day_of_the_week=self.cleaned_data.get('availability'),
                time_of_the_day=self.cleaned_data.get('time_of_lesson'),
                student=req.user,
                teacher=self.cleaned_data.get('teacher'),
                start_date=self.cleaned_data.get('start_date'),
                duration_of_lessons=self.cleaned_data.get('duration_of_lessons'),
                interval_between_lessons=self.cleaned_data.get('interval_between_lessons'),
                number_of_lessons=self.cleaned_data.get('number_of_lessons'),
                further_information=self.cleaned_data.get('further_information'),
                invoice_id="1234-123"
            )
            #request.availability.add(available_day)



            #booking.save()
            return [booking, req]
        else:
            print("Request already fulfilled")



class LogInForm(forms.Form):
    email = forms.CharField(label='Email')
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
            message='Password must contain an uppercase character, a lower case character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

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
        fields = ['date', 'amount']
        widgets = {
            'date': DateInput()
        }

    student_email = forms.EmailField(label='Student\'s email', required=False)
    invoice_number = forms.CharField(label='Invoice number', required=True)

    def clean(self):
        super().clean()
        student_email = self.cleaned_data.get('student_email')
        if(not(User.objects.filter(email=student_email).exists())):
            self.add_error('student_email', 'Student email does not exist in database.')

        invoice_no = self.cleaned_data.get('invoice_number')
        if(not(Invoice.objects.filter(invoice_number=invoice_no).exists())):
            self.add_error('invoice_number', 'Invoice number does not exist in database.')

    def save(self):
        super().save(commit=False)

        s_email = self.cleaned_data.get('student_email')
        student_user=User.objects.get(email=s_email)
        student=Student.objects.get(user=student_user)

        invoice_no = self.cleaned_data.get('invoice_number')
        invoice_obj = Invoice.objects.get(invoice_number=invoice_no)

        BankTransaction.objects.create(
            date=self.cleaned_data.get('date'),
            student=student,
            amount=self.cleaned_data.get('amount'),
            invoice=invoice_obj
        )

    def generate_invoice_num(self, student):
        # check student object to see the number of transactions that have been made by the student
        # get student id (primary key) from object
        # alter string so that it fits the form xxxx-yyy
        pass

