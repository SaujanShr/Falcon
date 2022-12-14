"""Tests of the director creation view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import CreateUser
from lessons.models import User
from lessons.tests.helpers import create_user_groups


class CreateDirectorUserViewTestCase(TestCase):
    """Tests of the director creation view."""

    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        create_user_groups()
        self.user = User.objects.get(email="johndoe@email.com")
        self.user.is_superuser = True
        self.user.save()
        self.url = reverse('create_director_user')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_director_creation_url(self):
        self.assertEqual(self.url, '/create_director_user/')

    def test_get_create_director_user(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'create_user.html') 
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateUser)) 
        self.assertFalse(form.is_bound)

    def test_unsuccessful_director_creation(self):
        self.client.login(email=self.user.email, password='Password123')
        self.form_input['email'] = 'NOT_AN_EMAIL'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_user.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, CreateUser))
        self.assertTrue(form.is_bound)

    def test_successful_director_creation(self):
        self.client.login(email=self.user.email, password='Password123')
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True) 
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('admin_user_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200) 
        self.assertTemplateUsed(response, 'admin_user_list.html')
        user = User.objects.get(email='janedoe@example.org')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertTrue(user.is_superuser)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
