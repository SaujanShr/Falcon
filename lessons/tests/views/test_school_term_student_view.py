"""Unit tests of the school term student view"""
import datetime
from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm
from django.db.models.query import QuerySet
from lessons.tests.helpers import HandleGroups, reverse_with_next


class SchoolTermStudentView(TestCase):
    """Unit tests of the school term student view"""

    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        self.client.login(email='johndoe@email.com', password='Password123')
        self.url = reverse('student_term_view')

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
        self.assertEqual(self.url, '/student_page/terms')

    def test_get_school_term_student_view_redirects_when_not_logged_in(self):
        self.client.logout()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_school_term_student_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_term_view.html')
        terms = response.context['terms']
        self.assertTrue(isinstance(terms, QuerySet))

    def test_school_terms_student_view_displays_all_terms(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_term_view.html')
        terms = response.context['terms']
        self.assertEqual(terms.all().count(), SchoolTerm.objects.count())
