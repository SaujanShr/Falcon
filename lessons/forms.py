from django import forms

from .models import DayOfTheWeek, Request, BankTransaction

class DateInput(forms.DateInput):
    input_type = 'date'
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

class LogInForm(forms.Form):
    email = forms.CharField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

class TransactionSubmitForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = ['date', 'student', 'amount', 'invoice_number']
        widgets = {
            'date': DateInput()
        }

    #TODO: generate invoice number automatically from student chosen, for now manually submit the invoice number, prone to error.

    def save(self):
        super().save(commit=False)
        BankTransaction.objects.create(
            date=self.cleaned_data.get('date'),
            student=self.cleaned_data.get('student'),
            amount=self.cleaned_data.get('amount'),
            invoice_number=self.cleaned_data.get('invoice_number')
        )


    def generate_invoice_num(self, student):
        #check student object to see the number of transactions that have been made by the student
        #get student id (primary key) from object
        #alter string so that it fits the form xxxx-yyy
        pass