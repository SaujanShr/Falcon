from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from django.db.models.query import QuerySet
from lessons.tests.helpers import create_user_groups


class AdminDashboardPageTestCase(TestCase):
    def setUp(self):
        create_user_groups()
        self.url = reverse('admin_page')

        self.superuser = User.objects.create_superuser(
            email='admin@email.com',
            password='password'
        )

    def test_admin_dashboard_url(self):
        self.assertEqual(self.url, '/admin_page/')

    def test_get_admin_dashboard(self):
        self.client.login(email='admin@email.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_page.html')
        transactions = response.context['transactions']
        self.assertTrue(isinstance(transactions, QuerySet))