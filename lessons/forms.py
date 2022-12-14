import decimal

from django import forms
from django.core.validators import RegexValidator, MinValueValidator
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

class ChildEditForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        self.instance_id = kwargs.pop('instance_id', None)
        super(ChildEditForm, self).__init__(*args, **kwargs)

    def save(self):
        instance_set = Child.objects.filter(id=self.instance_id)
        super().save(commit=False)
        instance_set.update(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name')
        )
        return instance_set[0]

class InvoiceEditForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_number', 'full_amount', 'paid_amount']

    student_name = forms.CharField(label="Student")

    #Invoices should never be edited manually, this form is purely for display.
    def __init__(self, *args, **kwargs):
        super(InvoiceEditForm, self).__init__(*args, **kwargs)
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

class RequestEditForm(forms.ModelForm):
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
        super(RequestEditForm, self).__init__(*args, **kwargs)

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
    class Meta:
        model = Booking
        fields = ['availability', 'number_of_lessons', 'interval_between_lessons',
                  'duration_of_lessons', 'further_information']
        widgets = {'further_information':forms.Textarea(attrs={'style': "width:100%;"})}

    field_order = ['availability', 'interval_between_lessons', 'number_of_lessons',
                   'duration_of_lessons', 'time_of_lesson', 'teacher',
                   'start_date', 'end_date', 'further_information', 'hourly_cost']

    def __init__(self, *args, **kwargs):
        self.request_id = kwargs.pop('request_id', None)

        super(FulfilRequestForm, self).__init__(*args, **kwargs)

        if self.request_id:
            user_request = Request.objects.get(id=self.request_id)
            self.fields['availability'] = forms.ModelChoiceField(
                queryset=user_request.availability.all(),
                label="Day of lessons:",
                widget=forms.Select
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
        label='End date:',
        widget=forms.DateInput(
            attrs={'type': 'date'}
        )
    )

    hourly_cost = forms.CharField(
        widget=forms.TextInput(
            attrs={'type':'decimal'}
        )
    )

    def save(self):
        super().save(commit=False)
        req = Request.objects.get(id=self.request_id)

        if not req.fulfilled:
            booking = Booking(
                time_of_the_day=self.cleaned_data.get('time_of_lesson'),
                day_of_the_week=self.cleaned_data.get('availability'),
                user=req.user,
                relation_id=req.relation_id,
                teacher=self.cleaned_data.get('teacher'),
                start_date=self.cleaned_data.get('start_date'),
                end_date=self.cleaned_data.get('end_date'),
                term_id=find_term_from_date(self.cleaned_data.get('start_date')),
                duration_of_lessons=self.cleaned_data.get('duration_of_lessons'),
                interval_between_lessons=self.cleaned_data.get('interval_between_lessons'),
                number_of_lessons=self.cleaned_data.get('number_of_lessons'),
                further_information=self.cleaned_data.get('further_information')
            )

            invoice_no = create_invoice(booking, self.cleaned_data.get('hourly_cost'))
            booking.invoice = Invoice.objects.get(invoice_number=invoice_no)

            req.fulfilled = True
            req.save()

            return booking.save()
        else:
            return None



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
        super().save(commit=False)
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
        super().save(commit=False)
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


class BookingEditForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['day_of_the_week','time_of_the_day','teacher','start_date',
                  'duration_of_lessons','interval_between_lessons','number_of_lessons',
                  'further_information']
        widgets = {'further_information':forms.Textarea(attrs={'style': "width:100%;"})}

    field_order = ['day_of_the_week', 'time_of_the_day', 'start_date', 'end_date',
                   'duration_of_lessons', 'interval_between_lessons', 'number_of_lessons',
                   'teacher', 'further_information', 'hourly_cost']

    day_of_the_week = forms.ModelChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Day of lessons:",
        widget=forms.Select
    )

    time_of_the_day = forms.TimeField(
        label='Lesson time:',
        widget=forms.TimeInput(
            attrs={'type': 'time'}
        ),
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
    end_date = forms.DateField(
        label='End date:',
        widget=forms.DateInput(
            attrs={'type': 'date'}
        )
    )
    hourly_cost = forms.CharField(
        widget=forms.TextInput(
            attrs={'type': 'decimal'},
        ),
        validators=[MinValueValidator('0.01')]
    )

    def __init__(self, *args, **kwargs):
        self.instance_id = kwargs.pop('instance_id', None)
        super(BookingEditForm, self).__init__(*args, **kwargs)

    def set_read_only(self):
        self.fields['day_of_the_week'].disabled = True
        self.fields['time_of_the_day'].disabled = True
        self.fields['teacher'].disabled = True
        self.fields['start_date'].disabled = True
        self.fields['end_date'].disabled = True
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
            end_date = self.cleaned_data.get('end_date'),
            duration_of_lessons = self.cleaned_data.get('duration_of_lessons'),
            interval_between_lessons = self.cleaned_data.get('interval_between_lessons'),
            number_of_lessons = self.cleaned_data.get('number_of_lessons'),
            further_information = self.cleaned_data.get('further_information')
        )


        # Update invoice
        student = Student.objects.get(user=instance_set[0].user)
        invoice = instance_set[0].invoice
        new_cost = instance_set[0].duration_of_lessons * float(self.cleaned_data.get('hourly_cost')) * instance_set[0].number_of_lessons / 60
        invoice.full_amount = new_cost

        if invoice.paid_amount > invoice.full_amount:
            student.balance = student.balance + decimal.Decimal(
                (invoice.paid_amount - decimal.Decimal(invoice.full_amount)))
            invoice.paid_amount = invoice.full_amount
            invoice.fully_paid = True
            student.save()
        elif invoice.paid_amount == invoice.full_amount:
            invoice.fully_paid = True
        else:
            invoice.fully_paid = False

        invoice.save()

        return instance_set[0]



class TermEditForm(forms.ModelForm):
    class Meta:
        model = SchoolTerm
        fields = ['term_name', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput()
        }
