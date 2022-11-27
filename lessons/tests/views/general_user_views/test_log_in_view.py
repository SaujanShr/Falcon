"""Tests of the log in view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from lessons.forms import LogInForm
from lessons.models import User
from lessons.tests.helpers import LogInTester, reverse_with_next,HandleGroups

class LogInViewTestCase(TestCase, LogInTester):
    """Tests of the log in view."""

    fixtures = ['lessons/tests/fixtures/default_user.json','lessons/tests/fixtures/other_users.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()
        self.url = reverse('log_in')
        self.user = User.objects.get(email='johndoe@email.com')

    def test_log_in_url(self):
        self.assertEqual(self.url, '/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(next)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_with_redirect(self):
        destination_url = reverse('redirect')
        self.url = reverse_with_next('log_in', destination_url)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destination_url)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_get_log_in_redirects_student_when_logged_in(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('student_page')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_unsuccessful_log_in(self):
        form_input = {'email': 'johndoe@email.com', 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_email(self):
        form_input = {'email': '', 'password': 'Password123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = {'email': 'johndoe@email.com', 'password': ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_successful_log_in_student(self):
        form_input = {'email': 'johndoe@email.com', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('student_page')
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
        
    def test_successful_log_in_admin(self):
        form_input = {'email': 'janedoe@email.com', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('admin_page')
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_page.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
    
    def test_successful_log_in_director(self):
        user = User.objects.get(email = "janedoe@email.com")
        user.is_staff=True
        form_input = {'email': 'janedoe@email.com', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('admin_page')
        self.assertRedirects(response, response_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_page.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_successful_log_in_with_redirect(self):
        redirect_url = reverse('student_page')
        form_input = {'email': 'johndoe@email.com',
                      'password': 'Password123', 'next': redirect_url}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)

    def test_post_log_in_redirects_student_when_logged_in(self):
        redirect_url = reverse('student_page')
        self.client.login(email=self.user.email,
                          password="WrongPassword")
        form_input = {'email': 'johndoe@email.com',
                      'password': 'Password123', 'next': redirect_url}
        response = self.client.post(self.url, form_input, follow=True)

        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_post_log_in_redirects_admin_when_logged_in(self):
        redirect_url = reverse('redirect')
        self.client.login(email=self.user.email,
                          password="WrongPassword")
        form_input = {'email': 'janedoe@email.com',
                      'password': 'Password123', 'next': redirect_url}
        response = self.client.post(self.url, form_input, follow=True)

        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'test_redirect.html')

    def test_valid_log_in_by_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form_input = {'email': 'johndoe@email.com', 'password': 'Password123'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
