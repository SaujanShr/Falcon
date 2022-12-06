"""Tests of the admin user list view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from lessons.tests.helpers import HandleGroups
from django.conf import settings

class AdminUserListTestCase(TestCase):
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        self.url = reverse('admin_user_list')
        self.user = User.objects.get(email='johndoe@email.com')
        self.other_user = User.objects.get(email="janedoe@email.com")
        self.user.is_superuser = True
        self.user.save()

    def test_log_out_url(self):
        self.assertEqual(self.url, '/admin_user_list/')

    def test_get_admin_user_list(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'admin_user_list.html') 

    def test_edit_button_redirects_to_edit_page(self):
        self.client.login(email=self.user.email, password='Password123')
        payload = {'edit': self.user.id}
        response = self.client.post(self.url,payload, follow=True)
        redirect_url = f'{reverse("profile")}?user_id={str(self.user.id)}'
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_admin_user_list_only_accessible_to_director(self):
        HandleGroups.set_other_user_to_student()
        self.client.login(email=self.other_user.email, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT)
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)

    def test_promote_to_director_button_makes_user_director(self):
        HandleGroups.set_other_user_to_student()
        self.assertEqual(self.other_user.get_group(),"Student")
        self.client.login(email=self.user.email, password='Password123')
        payload = {'promote_director': self.other_user.id}
        response = self.client.post(self.url,payload)
        self.assertTemplateUsed(response, 'admin_user_list.html')
        other_user_after_request = User.objects.get(id=self.other_user.id)
        self.assertTrue(other_user_after_request.is_superuser)

    def test_delete_button_deleted_user(self):
        self.client.login(email=self.user.email, password='Password123')
        other_user_id = self.other_user.id
        payload = {'delete': other_user_id}
        response = self.client.post(self.url, payload)
        self.assertTemplateUsed(response, 'admin_user_list.html')
        self.assertEqual(User.objects.filter(id = other_user_id).count(),0)

    def test_create_student_button_redirects(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url,{'create_student':''}, follow=True)
        redirect_url = reverse('create_student_user')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'create_user.html')

    def test_create_director_button_redirects(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url,{'create_director':''}, follow=True)
        redirect_url = reverse('create_director_user')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'create_user.html')

    def test_create_administrator_button_redirects(self):
        self.client.login(email=self.user.email, password='Password123')
        response = self.client.post(self.url,{'create_administrator':''}, follow=True)
        redirect_url = reverse('create_admin_user')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'create_user.html')