from django.test import TestCase
from django.urls import reverse
from lessons.models import BankTransaction, User, Student
from django.db.models.query import QuerySet
from lessons.tests.helpers import create_user_groups

class TransactionAdminListTestCase(TestCase):
    def setUp(self):
        create_user_groups()
        self.url = reverse('transaction_list_student')
        self.user = User.objects.create_user(
                email='email1@email.com',
                password='password'
            )
        self.student = Student.objects.create(user = self.user)

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/student')

    def test_get_transaction_student_view(self):
        self.client.login(email='email1@email.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_list.html')
        transactions = response.context['transactions']
        self.assertTrue(isinstance(transactions, QuerySet))

    #TODO more tests for the transaction list view

    def test_transaction_student_displays_only_students_transactions(self):
        pass

    def test_transaction_student_displays_correct_fields(self):
        pass

    def test_transaction_student_displays_correct_data(self):
        pass