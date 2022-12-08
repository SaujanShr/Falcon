"""Tests of the sign-up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import SignUpForm
from lessons.models import User
from lessons.tests.helpers import create_user_groups


class SignUpViewTestCase(TestCase):
    """Tests of the sign-up view"""

    def setUp(self):
        create_user_groups()

        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'NOT_AN_EMAIL'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        user = User.objects.get(email='janedoe@example.org')
        
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
