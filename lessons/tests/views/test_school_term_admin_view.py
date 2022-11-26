"""Unit tests of the school term admin view"""
import datetime
from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm
from django.db.models.query import QuerySet
from lessons.tests.helpers import HandleGroups


class SchoolTermStudentView(TestCase):
    """Unit tests of the school term admin view"""

    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()
        self.url = reverse('admin_term_view')

        self.client.login(email='janedoe@email.com', password='Password123')
        self.term1 = SchoolTerm.objects.create(
            term_name="Term one",
            start_date=datetime.date(2022, 1, 1),
            end_date=datetime.date(2022, 12, 31)
        )

        self.term2 = SchoolTerm.objects.create(
            term_name="Term two",
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 12, 31)
        )

    def test_school_term_student_view_url(self):
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
        response = self.client.get(self.url)

        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        #self.assertTemplateUsed(response, 'student_page.html') #This doesn't work properly

