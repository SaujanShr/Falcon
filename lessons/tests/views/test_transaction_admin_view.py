from django.test import TestCase
from django.urls import reverse
from lessons.forms import TransactionSubmitForm
from lessons.models import BankTransaction, User, Student, Invoice
from django.contrib.auth.models import Group
from decimal import Decimal
import datetime
from lessons.tests.helpers import create_user_groups

class TransactionAdminViewTestCase(TestCase):
    def setUp(self):
        create_user_groups()
        self.url = reverse('transaction_admin_view')
        self.user = User.objects.create_user(
                email='email1@email.com',
                password='password'
            )
        self.student = Student.objects.create(user = self.user)
        self.invoice1 = Invoice.objects.create(
            invoice_number='1234-123',
            student=self.student,
            full_amount='100.00'
        )
        self.form_input = {
            'date': datetime.date.today(),
            'student_email': self.user.email,
            'amount': '3.14',
            'invoice_number': '1234-123'
        }

        self.superuser = User.objects.create_superuser(
            email='admin@email.com',
            password='password'
        )

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/admin/submit')

    def test_get_transaction_admin_view(self):
        self.client.login(email='admin@email.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        self.assertFalse(form.is_bound)

    def test_invalid_transaction_entered(self):
        self.client.login(email='admin@email.com', password='password')
        self.form_input['invoice_number'] = '123-1234'
        before_count = BankTransaction.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = BankTransaction.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        self.assertTrue(form.is_bound)
    
    
    def test_valid_transaction_entered(self):
        self.client.login(email='admin@email.com', password='password')
        before_count = BankTransaction.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = BankTransaction.objects.count()
        self.assertEqual(before_count+1, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        transaction = BankTransaction.objects.get(invoice=self.invoice1)
        amount_in_decimal = Decimal(self.form_input['amount'].replace(',','.'))
        self.assertEqual(transaction.date, self.form_input['date'])
        self.assertEqual(transaction.student, self.student)
        self.assertEqual(transaction.amount, amount_in_decimal)
        self.assertEqual(transaction.invoice, self.invoice1) 

