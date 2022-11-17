from django.test import TestCase
from django.urls import reverse
from lessons.models import BankTransaction, User, Student
from django.db.models.query import QuerySet

class TransactionAdminListTestCase(TestCase):
    def setUp(self):
        self.url = reverse('balance_list_admin')
        self.user = User.objects.create_user(
                email='email1@email.com',
                password='password'
            )
        self.student = Student.objects.create(user = self.user)

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/balance/admin')

    def test_get_transaction_student_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'balance_list.html')
        students = response.context['students']
        self.assertTrue(isinstance(students, QuerySet))

    #TODO more tests for the balance list view


    def test_balance_view_displays_correct_fields(self):
        pass
    
    def test_balance_view_displays_all_students(self):
        pass

    def test_balance_view_displays_correct_balances(self):
        pass