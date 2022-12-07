"""Unit tests of the log in form."""
from django import forms
from django.test import TestCase
from lessons.forms import LogInForm
from lessons.models import User
from django.contrib.auth.models import Group
from django.urls import reverse
from lessons.tests.helpers import HandleGroups,LogInTester
from django.conf import settings

class LogInFormTestCase(TestCase,LogInTester):
    """Unit tests of the log in form."""
    fixtures = ['lessons/tests/fixtures/default_user.json','lessons/tests/fixtures/other_users.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()
        self.default_user = User.objects.get(email = "johndoe@email.com")
        self.other_user = User.objects.get(email = "janedoe@email.com")
    
    def test_login_prohibited_handles_user_with_no_group(self):
        user_with_no_group = User.objects.get(email="bobdylan@email.com")
        self.client.login(email=user_with_no_group.email,
                          password="Password123")
        response = self.client.get(reverse('log_in'),follow=True)
        self.assertRedirects(response,reverse('home'),status_code=302,target_status_code=200)
        self.assertFalse(self._is_logged_in())
    
    def test_login_prohibited_handles_student_user(self):
        self.client.login(email=self.default_user.email,
                          password="Password123")
        response = self.client.get(reverse('log_in'),follow=True)
        self.assertRedirects(response,reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT),status_code=302,target_status_code=200)

    def test_login_prohibited_handles_admin_user(self):
        self.client.login(email=self.other_user.email,
                          password="Password123")
        response = self.client.get(reverse('log_in'),follow=True)
        self.assertRedirects(response,reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_ADMIN),status_code=302,target_status_code=200)

    def test_login_prohibited_handles_director_user(self):
        user_with_no_group = User.objects.get(email="bobdylan@email.com")
        user_with_no_group.is_superuser = True
        user_with_no_group.save()
        self.client.login(email=self.other_user.email,
                          password="Password123")
        response = self.client.get(reverse('log_in'),follow=True)
        self.assertRedirects(response,reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_DIRECTOR),status_code=302,target_status_code=200)