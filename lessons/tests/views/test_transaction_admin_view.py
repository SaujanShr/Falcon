from django.test import TestCase
from django.urls import reverse
from lessons.forms import TransactionSubmitForm
from lessons.models import BankTransaction, User, Student
from decimal import Decimal
import datetime
from lessons.tests.helpers import HandleGroups

class TransactionAdminViewTestCase(TestCase):

    fixtures = ['lessons/tests/fixtures/other_users.json','lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.url = reverse('transaction_admin_view')
        self.user = User.objects.get(email='janedoe@email.com')
        self.student_user = User.objects.get(email='johndoe@email.com')
        HandleGroups.set_other_user_to_admin()
        self.student = Student.objects.create(user = self.student_user)
        self.form_input = {
            'date': datetime.date.today(),
            'student_email': self.student_user.email,
            'amount': '3.14',
            'invoice_number': '1234-123'
        }

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/admin/submit')

    def test_get_transaction_admin_view(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        self.assertFalse(form.is_bound)

    def test_invalid_transaction_entered(self):
        self.client.login(email=self.user.email, password='Password123')
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
        self.client.login(email=self.user.email, password='Password123')
        before_count = BankTransaction.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = BankTransaction.objects.count()
        self.assertEqual(before_count+1, after_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_admin_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TransactionSubmitForm))
        transaction = BankTransaction.objects.get(invoice_number='1234-123')
        amount_in_decimal = Decimal(self.form_input['amount'].replace(',','.'))
        self.assertEqual(transaction.date, self.form_input['date'])
        self.assertEqual(transaction.student, self.student)
        self.assertEqual(transaction.amount, amount_in_decimal)
        self.assertEqual(transaction.invoice_number, self.form_input['invoice_number']) 

