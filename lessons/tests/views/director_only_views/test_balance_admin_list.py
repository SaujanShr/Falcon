from django.test import TestCase
from django.urls import reverse
from lessons.models import BankTransaction, User, Student
from django.db.models.query import QuerySet
from django.contrib.auth.models import Group
from lessons.tests.helpers import create_user_groups

class TransactionAdminListTestCase(TestCase):

    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        create_user_groups()
        self.john_doe_user = User.objects.get(email='johndoe@email.com')
        self.jane_doe_user = User.objects.get(email='janedoe@email.com')
        self.url = reverse('balance_list_admin')
        self.student = Student.objects.create(user = self.john_doe_user)
        self.student2 = Student.objects.create(user = self.jane_doe_user)
        self.superuser = User.objects.create_superuser(
            email='admin@email.com',
            password='password'
        )

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/balance/admin')

    def test_get_balance_admin_view(self):
        self.client.login(email='admin@email.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'balance_list.html')
        students = response.context['students']
        self.assertTrue(isinstance(students, QuerySet))

    def test_balance_view_displays_all_students(self):
        self.client.login(email='admin@email.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'balance_list.html')
        students = response.context['students']
        self.assertEqual(students.all().count(), Student.objects.count())