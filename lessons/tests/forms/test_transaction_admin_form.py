from django.test import TestCase
from django import forms
from lessons.models import BankTransaction, User
from lessons.forms import TransactionSubmitForm
import datetime

class TransactionFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                email='email1@email.com',
                password='password'
            )
        self.form_input = {
            'date': datetime.date.today(),
            'student': self.user,
            'amount': '3.14',
            'invoice_number': '1234-123'
        }

    def test_valid_sign_up_form(self):
        
        form = TransactionSubmitForm(data=self.form_input)
        self.assertFalse(form.errors)

    def test_transaction_form_has_necessary_fields(self):
        form = TransactionSubmitForm()
        self.assertIn('date', form.fields)
        date_widget = form.fields['date'].widget
        self.assertTrue(isinstance(date_widget, forms.DateInput))
        self.assertIn('student', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('invoice_number', form.fields)

    def test_transaction_from_uses_model_validation(self):
        self.form_input['invoice_number'] = '123-1234'
        form = TransactionSubmitForm(data=self.form_input)
        self.assertFalse(form.is_valid())
