"""Unit tests of the school term admin view"""
from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm
from django.db.models.query import QuerySet
from lessons.tests.helpers import HandleGroups, reverse_with_next


class SchoolTermStudentView(TestCase):
    """Unit tests of the school term admin view"""

    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_terms.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()
        self.url = reverse('admin_term_view')

        self.client.login(email='janedoe@email.com', password='Password123')

        self.term1 = SchoolTerm.objects.get(id=1)
        self.term2 = SchoolTerm.objects.get(id=2)

    def test_school_term_admin_view_url(self):
        self.assertEqual(self.url, '/admin_term_view')

    def test_get_school_term_admin_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_term_view.html')
        terms = response.context['terms']
        self.assertTrue(isinstance(terms, QuerySet))

    def test_school_terms_admin_view_displays_all_terms(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_term_view.html')
        terms = response.context['terms']
        self.assertEqual(terms.all().count(), SchoolTerm.objects.count())

    def test_student_cannot_access_school_terms_admin_view(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url, follow=True)

        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_get_school_term_edit_redirects_when_not_logged_in(self):
        self.client.logout()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)