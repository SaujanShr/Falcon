from django.test import TestCase
from django.urls import reverse
from lessons.models import BankTransaction, User, Student
from django.db.models.query import QuerySet
from lessons.tests.helpers import create_user_groups

class TransactionAdminListTestCase(TestCase):
    def setUp(self):
        create_user_groups()
        self.url = reverse('transaction_list_admin')
        self.user = User.objects.create_user(
                email='email1@email.com',
                password='password'
            )
        self.student = Student.objects.create(user = self.user)

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/admin/view')

    def test_get_transaction_admin_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_list.html')
        transactions = response.context['transactions']
        self.assertTrue(isinstance(transactions, QuerySet))

    #TODO more tests for the transaction list view

    def test_transaction_admin_displays_all_transactions(self):
        pass

    def test_transaction_admin_displays_correct_fields(self):
        pass

    def test_transaction_admin_displays_correct_data(self):
        pass