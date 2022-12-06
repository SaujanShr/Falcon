from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group
from .models import User, Child, DayOfTheWeek, Request, BankTransaction, Student, Invoice, SchoolTerm, Booking
from .forms_functions import create_invoice, find_term_from_date


class DateInput(forms.DateInput):
    input_type = 'date'

class NewChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(NewChildForm, self).__init__(*args, **kwargs)
    
    def save(self):
        child = super().save(commit=False)
        child.parent = self.user
        return child.save()

class ChildViewForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        self.instance_id = kwargs.pop('instance_id', None)
        super(ChildViewForm, self).__init__(*args, **kwargs)
    
    def save(self):
        instance_set = Child.objects.filter(id=self.instance_id)
        super().save(commit=False)
        instance_set.update(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name')
        )
        return instance_set[0]

class InvoiceViewForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'full_amount', 'paid_amount']

    student_name = forms.CharField(label="Student")

    #Invoices should never be edited manually, this form is purely for display.
    def __init__(self, *args, **kwargs):
        super(InvoiceViewForm, self).__init__(*args, **kwargs)
        self.fields['invoice_number'].disabled = True
        self.fields['student_name'].disabled = True
        self.fields['full_amount'].disabled = True
        self.fields['paid_amount'].disabled = True
    



class NewRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['availability', 'number_of_lessons',
                  'interval_between_lessons', 'duration_of_lessons', 'further_information']
        widgets = {'further_information':forms.Textarea(attrs={'style': "width:100%;"})}

    availability = forms.ModelMultipleChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Available Days",
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.relation_id = kwargs.pop('relation_id', None)
        super(NewRequestForm, self).__init__(*args, **kwargs)
        
    def save(self):
        request = super().save(commit=False)
        request.user = self.user
        request.relation_id = self.relation_id
        
        res = request.save()
        request.availability.set(self.cleaned_data.get('availability'))
        
        return res 

class RequestViewForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['date', 'availability', 'number_of_lessons', 'interval_between_lessons', 
                  'duration_of_lessons', 'further_information', 'fulfilled']
        widgets = {'further_information':forms.Textarea(attrs={'style': "width:100%;"})}

    availability = forms.ModelMultipleChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Available Days",
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, *args, **kwargs):
        self.instance_id = kwargs.pop('instance_id', None)
        super(RequestViewForm, self).__init__(*args, **kwargs)
        
        self.fields['date'].disabled = True
        self.fields['fulfilled'].disabled = True

    def set_read_only(self):
        self.fields['availability'].disabled = True
        self.fields['number_of_lessons'].disabled = True
        self.fields['interval_between_lessons'].disabled = True
        self.fields['duration_of_lessons'].disabled = True
        self.fields['further_information'].disabled = True
    
    def save(self):
        instance_set = Request.objects.filter(id=self.instance_id)
        super().save(commit=False)
        
        instance_set.update(
            number_of_lessons=self.cleaned_data.get('number_of_lessons'),
            interval_between_lessons=self.cleaned_data.get('interval_between_lessons'),
            duration_of_lessons=self.cleaned_data.get('duration_of_lessons'),
            further_information=self.cleaned_data.get('further_information'),
        )
        instance_set[0].availability.set(self.cleaned_data.get('availability'))
        
        return instance_set[0]


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
        widgets = {'further_information':forms.Textarea(attrs={'style': "width:100%;"})}

    field_order = ['availability', 'interval_between_lessons', 'number_of_lessons',
                   'duration_of_lessons', 'time_of_lesson', 'teacher', 'hourly_cost',
                   'start_date', 'end_date', 'further_information']

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

    end_date = forms.DateField(
        label='End date (leave empty for last day of term):',
        widget=forms.DateInput(
            attrs={'type': 'date'}
        )
    )

    hourly_cost = forms.CharField(
        widget=forms.TextInput(
            attrs={'type':'number'}
        )
    )

    def save(self):
        super().save(commit=False)
        req = Request.objects.get(date=self.cleaned_data.get('date'))
        if not req.fulfilled:
            booking = Booking(
                time_of_the_day=self.cleaned_data.get('time_of_lesson'),
                day_of_the_week=self.cleaned_data.get('availability'),
                user=req.user,
                relation_id=req.relation_id,
                teacher=self.cleaned_data.get('teacher'),
                start_date=self.cleaned_data.get('start_date'),
                end_date=self.cleaned_data.get('end_date'),
                duration_of_lessons=self.cleaned_data.get('duration_of_lessons'),
                interval_between_lessons=self.cleaned_data.get('interval_between_lessons'),
                number_of_lessons=self.cleaned_data.get('number_of_lessons'),
                further_information=self.cleaned_data.get('further_information')
            )

            return [booking, req, self.cleaned_data.get('hourly_cost')]
        else:
            return [None, req]



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

class CreateUser(forms.ModelForm):
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
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class PasswordForm(forms.Form):

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='New Password Confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


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

class BookingViewForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['day_of_the_week','time_of_the_day','teacher','start_date',
                  'duration_of_lessons','interval_between_lessons','number_of_lessons',
                  'further_information']
        widgets = {'further_information':forms.Textarea(attrs={'style': "width:100%;"})}

    day_of_the_week = forms.ModelChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Day of lessons:",
        widget=forms.Select
    )

    time_of_the_day = forms.TimeField(
        label='Lesson time:',
        widget=forms.TimeInput(
            attrs={'type': 'time'}
        )
    )
    teacher = forms.CharField(
        label='Teacher:',
        widget=forms.TextInput
    )
    start_date = forms.DateField(
        label='Start date:',
        widget=forms.DateInput(
            attrs={'type': 'date'}
        )
    )
    hourly_cost = forms.CharField(
        widget=forms.TextInput(
            attrs={'type': 'number'}
        )
    )
    
    def __init__(self, *args, **kwargs):
        self.instance_id = kwargs.pop('instance_id', None)
        super(BookingViewForm, self).__init__(*args, **kwargs)
    
    def set_read_only(self):
        self.fields['invoice_id'].disabled = True
        self.fields['day_of_the_week'].disabled = True
        self.fields['time_of_the_day'].disabled = True
        self.fields['teacher'].disabled = True
        self.fields['start_date'].disabled = True
        self.fields['duration_of_lessons'].disabled = True
        self.fields['interval_between_lessons'].disabled = True
        self.fields['number_of_lessons'].disabled = True
        self.fields['further_information'].disabled = True
        self.fields['hourly_cost'].disabled = True
    
    def save(self):
        instance_set = Booking.objects.filter(id=self.instance_id)
        super().save(commit=False)
        
        instance_set.update(
            day_of_the_week = self.cleaned_data.get('day_of_the_week'),
            time_of_the_day = self.cleaned_data.get('time_of_the_day'),
            teacher = self.cleaned_data.get('teacher'),
            start_date = self.cleaned_data.get('start_date'),
            duration_of_lessons = self.cleaned_data.get('duration_of_lessons'),
            interval_between_lessons = self.cleaned_data.get('interval_between_lessons'),
            number_of_lessons = self.cleaned_data.get('number_of_lessons'),
            further_information = self.cleaned_data.get('further_information')
        )
        
        return instance_set[0]
        


class TermViewForm(forms.ModelForm):
    class Meta:
        model = SchoolTerm
        fields = ['term_name', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput()
        }
