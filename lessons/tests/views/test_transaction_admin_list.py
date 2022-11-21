from django.test import TestCase
from django.urls import reverse
from lessons.models import BankTransaction, User, Student
from django.db.models.query import QuerySet
from lessons.tests.helpers import HandleGroups

class TransactionAdminListTestCase(TestCase):

    fixtures = ['lessons/tests/fixtures/other_users.json','lessons/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('transaction_list_admin')
        self.user = User.objects.get(email='janedoe@email.com')
        self.student_user = User.objects.get(email='johndoe@email.com')
        HandleGroups.set_other_user_to_admin()
        self.student = Student.objects.create(user = self.student_user)

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/admin/view')

    def test_get_transaction_admin_list(self):
        self.client.login(email=self.user.email, password='Password123')
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