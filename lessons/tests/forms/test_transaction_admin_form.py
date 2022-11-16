from decimal import Decimal
from django.test import TestCase
from django import forms
from lessons.models import BankTransaction, User, Student
from lessons.forms import TransactionSubmitForm
import datetime

class TransactionFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                email='email1@email.com',
                password='password'
            )
        self.student = Student.objects.create(user = self.user)
        self.form_input = {
            'date': datetime.date.today(),
            'student': self.student,
            'amount': '3.14',
            'invoice_number': '1234-123'
        }

    def test_valid_transaction_form(self):
        form = TransactionSubmitForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_transaction_form_has_necessary_fields(self):
        form = TransactionSubmitForm()
        self.assertIn('date', form.fields)
        date_widget = form.fields['date'].widget
        self.assertTrue(isinstance(date_widget, forms.DateInput))
        self.assertIn('student', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('invoice_number', form.fields)

    def test_transaction_form_uses_model_validation(self):
        self.form_input['invoice_number'] = '123-1234'
        form = TransactionSubmitForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_transaction_form_saves_correctly(self):
        form = TransactionSubmitForm(data=self.form_input)
        before_count = BankTransaction.objects.count()
        form.save()
        after_count = BankTransaction.objects.count()
        self.assertEqual(before_count+1, after_count)
        transaction = BankTransaction.objects.get(invoice_number='1234-123')
        amount_in_decimal = Decimal(self.form_input['amount'].replace(',','.'))
        self.assertEqual(transaction.date, self.form_input['date'])
        self.assertEqual(transaction.student, self.form_input['student'])
        self.assertEqual(transaction.amount, amount_in_decimal)
        self.assertEqual(transaction.invoice_number, self.form_input['invoice_number']) 

    def test_user_balance_gets_updated(self):
        form = TransactionSubmitForm(data=self.form_input)
        before_count = BankTransaction.objects.count()
        form.save()
        after_count = BankTransaction.objects.count()
        self.assertEqual(before_count+1, after_count)
        student=Student.objects.get(user=self.user)
        amount_in_decimal = Decimal(self.form_input['amount'].replace(',','.'))
        self.assertEqual(student.balance, amount_in_decimal)
        pass

