from django.test import TestCase
from django.urls import reverse
from lessons.forms import TransactionSubmitForm
from lessons.models import BankTransaction, User, Student
import datetime

class TransactionAdminViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('transaction_admin_view')
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

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/admin')

    def test_get_transaction_admin_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        self.assertFalse(form.is_bound)

    def test_invalid_transaction_entered(self):
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
    
    """
    def test_valid_transaction_entered(self):
        before_count = BankTransaction.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = BankTransaction.objects.count()
        self.assertEqual(before_count+1, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        transaction = BankTransaction.objects.get(invoice_number='1234-123')
        self.assertEqual(transaction.date, self.form_input['date'])
        self.assertEqual(transaction.student, self.form_input['student'])
        self.assertEqual(transaction.amount, self.form_input['amount'])
        self.assertEqual(transaction.invoice_number, self.form_input['invoice_number']) 
    """
