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
        self.assertEqual(response.status_code, 200) # Check that the response status code is 200.
        self.assertTemplateUsed(response, 'sign_up.html') # Check that the template rendered is in the for of sign_up.html
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm)) # Check that the form is in the form of SignUpForm
        self.assertFalse(form.is_bound)

    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'NOT_AN_EMAIL'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)  # Check that the user count is the same, as we expect no user to be created.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True) # Follow = It makes sure that we follow the redirect.
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1) # Check that the user count has increased by 1
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200) # response_url = the url to be redirected to, status_code= what status code should be returned, target_status_code = The status code of the eventual code after the redirect.
        self.assertTemplateUsed(response, 'log_in.html')
        user = User.objects.get(email='janedoe@example.org')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', user.password) # Uses check_password as the password stored is a hash, using this will allow us to compare whether the given password is the same as the one stored as a hash.
        self.assertTrue(is_password_correct)
