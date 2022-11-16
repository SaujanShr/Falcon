from django.test import TestCase
from django.urls import reverse
from lessons.forms import TransactionSubmitForm
from lessons.models import BankTransaction, User
import datetime

class TransactionAdminViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('transaction_admin_view')
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

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/admin')

    def test_get_transaction_admin_view(self):
        url = self.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        self.assertFalse(form.is_bound)

    def test_invalid_transaction_entered(self):
        self.form_input['invoice_number'] = '123-1234'
        url = self.url
        response = self.client.post(url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        self.assertTrue(form.is_bound)

    """    def test_valid_transaction_entered(self):
        url = self.url
        response = self.client.post(url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        #self.assertFalse(form.is_bound)
        transaction = BankTransaction.objects.get(invoice_number=self.form_input['invoice_number'])
        self.assertEqual(transaction.date, self.form_input['date'])
        self.assertEqual(transaction.student, self.form_input['student'])
        self.assertEqual(transaction.amount, self.form_input['amount'])
        self.assertEqual(transaction.invoice_number, self.form_input['invoice_number']) """
