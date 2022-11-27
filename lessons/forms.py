from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group
from .models import User, Child, DayOfTheWeek, Request, BankTransaction, Student, Invoice
from django.utils import timezone

class DateInput(forms.DateInput):
    input_type = 'date'

class NewChildForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    
    def __init__(self, parent, *args, **kwargs):
        super(NewChildForm, self).__init__(*args, **kwargs)
        
        if parent:
            self.parent = parent
    
    def save(self):
        super().save(commit=False)
        fullname = self.cleaned_data.get('first_name') + ' ' + self.cleaned_data.get('last_name')
        child = Child.objects.create(
            parent=self.parent,
            fullname=fullname
        )
        return child
        
class NewRequestViewForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['student_name', 'availability', 'number_of_lessons',
                  'interval_between_lessons', 'duration_of_lessons', 'further_information']

    availability = forms.ModelMultipleChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Available Days",
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, user=None, *args, **kwargs): 
        super(NewRequestViewForm, self).__init__(*args, **kwargs)
        
        if user:
            self.user = user
            student_names = []
            student_names.append(('Me', 'Me'))
            
            for child in Child.objects.filter(parent=self.user):
                student_names.append(child.fullname, child.fullname)
                
            self.fields['student_name'] = forms.ChoiceField(
                choices=student_names,
                initial=student_names[0]
            )
    
    def save(self):
        super().save(commit=False)
        request = Request.objects.create(
            date=timezone.datetime.now(tz=timezone.utc),
            user=self.user,
            student_name=self.cleaned_data.get('student_name'),
            number_of_lessons=self.cleaned_data.get('number_of_lessons'),
            interval_between_lessons=self.cleaned_data.get('interval_between_lessons'),
            duration_of_lessons=self.cleaned_data.get('duration_of_lessons'),
            further_information=self.cleaned_data.get('further_information')
        )
        request.availability.set(self.cleaned_data.get('availability'))
        return request
        
    

class RequestViewForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['date', 'student_name', 'availability', 'number_of_lessons', 'interval_between_lessons',
                  'duration_of_lessons', 'further_information', 'fulfilled']

    availability = forms.ModelMultipleChoiceField(
        queryset=DayOfTheWeek.objects.all(),
        label="Available Days",
        widget=forms.CheckboxSelectMultiple
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super(RequestViewForm, self).__init__(*args, **kwargs)
        self.fields['date'].disabled = True
        self.fields['fulfilled'].disabled = True
        
        if user:
            self.user = user
            student_names = []
            student_names.append(('Me', 'Me'))
            
            for child in Child.objects.filter(parent=self.user):
                student_names.append(child.fullname, child.fullname)
                
            self.fields['student_name'] = forms.ChoiceField(
                choices=student_names,
                initial=student_names[0]
            )
    
    def set_read_only(self):
        self.fields['availability'].disabled = True
        self.fields['student_name'].disabled = True
        self.fields['number_of_lessons'].disabled = True
        self.fields['interval_between_lessons'].disabled = True
        self.fields['duration_of_lessons'].disabled = True
        self.fields['further_information'].disabled = True
    
    def save(self):
        self.fields['date'].disabled = False
        self.fields['fulfilled'].disabled = False
        
        return super().save(commit=True)


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

