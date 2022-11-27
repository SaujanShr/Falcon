from django.test import TestCase
from django.urls import reverse
#from lessons.forms import TransactionSubmitForm
from lessons.models import User
from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
#from decimal import Decimal
#import datetime
from lessons.tests.helpers import create_user_groups

class AdminDashboardPageTestCase(TestCase):
    def setUp(self):
        create_user_groups()
        self.url = reverse('admin_page')

        self.superuser = User.objects.create_superuser(
            email='admin@email.com',
            password='password'
        )

    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/admin_page/')

    def test_get_transaction_admin_view(self):
        self.client.login(email='admin@email.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_page.html')
        transactions = response.context['transactions']
        self.assertTrue(isinstance(transactions, QuerySet))