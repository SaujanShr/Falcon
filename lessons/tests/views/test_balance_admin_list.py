from django.test import TestCase
from django.urls import reverse
from lessons.models import BankTransaction, User, Student
from django.db.models.query import QuerySet
from lessons.tests.helpers import HandleGroups

class TransactionAdminListTestCase(TestCase):

    fixtures = ['lessons/tests/fixtures/other_users.json','lessons/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('balance_list_admin')
        self.user = User.objects.get(email='janedoe@email.com')
        self.student_user = User.objects.get(email='johndoe@email.com')
        HandleGroups.set_other_user_to_admin()
        self.student = Student.objects.create(user = self.student_user)

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/balance/admin')

    def test_get_transaction_student_view(self):
        self.client.login(email=self.user.email, password='Password123')
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