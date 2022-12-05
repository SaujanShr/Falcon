"""Unit tests of the decorator."""
from django.test import TestCase
from lessons.models import User
from django.urls import reverse
from lessons.tests.helpers import HandleGroups


class DecoratorTestCase(TestCase):
    """Unit tests of the decorator."""
    fixtures = ['lessons/tests/fixtures/default_user.json','lessons/tests/fixtures/other_users.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()
        HandleGroups.set_director_groups()
        self.default_user = User.objects.get(email = "johndoe@email.com")
        self.other_user = User.objects.get(email = "janedoe@email.com")

    def test_student_user_can_not_access_admin_only_page(self):
        self.client.login(email=self.default_user.email,
                          password="Password123")
        admin_only_page_url = reverse('redirect')
        response = self.client.get(admin_only_page_url, follow=True)
        redirect_url = reverse('student_page')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')
        
    def test_student_user_can_access_authorized_page(self):
        self.client.login(email=self.default_user.email,
                          password="Password123")
        authorized_page_url = reverse('student_page')
        response = self.client.get(authorized_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_admin_user_can_not_access_student_only_page(self):
        self.client.login(email=self.other_user.email,
                          password="Password123")
        student_only_page_url = reverse('student_page')
        response = self.client.get(student_only_page_url, follow=True)
        redirect_url = reverse('admin_page')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_page.html')

    def test_admin_user_can_access_authorized_page(self):
        self.client.login(email=self.other_user.email,
                          password="Password123")
        authorized_page_url = reverse('redirect')
        response = self.client.get(authorized_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'test_redirect.html')

    def test_director_user_can_access_authorized_page(self):
        self.client.login(email="director@email.com", password="Password123")
        authorized_page_url = reverse('create_admin_user')
        response = self.client.get(authorized_page_url)
        #print(response)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_user.html')

    def test_director_user_gets_redirected(self):
        self.client.login(email="director@email.com", password="Password123")
        authorized_page_url = reverse('log_in')
        response = self.client.get(authorized_page_url, follow=True)
        redirect_url = reverse('admin_page')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_page.html')
