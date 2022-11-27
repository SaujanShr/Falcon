"""Tests of the log out view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from lessons.tests.helpers import LogInTester, HandleGroups

class LogOutViewTestCase(TestCase, LogInTester):
    """Tests of the log out view."""

    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()
        self.url = reverse('log_out')
        self.student_user = User.objects.get(email='johndoe@email.com')
        self.admin_user = User.objects.get(email='janedoe@email.com')

    def test_log_out_url(self):
        self.assertEqual(self.url, '/log_out/')

    def test_student_log_out(self):
        self.client.login(email=self.student_user.email, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())

    def test_admin_log_out(self):
        self.client.login(email=self.admin_user.email, password='Password123')
        self.assertTrue(self._is_logged_in())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertFalse(self._is_logged_in())