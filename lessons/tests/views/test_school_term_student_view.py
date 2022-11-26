"""Unit tests of the school term student view"""
import datetime
from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm
from django.db.models.query import QuerySet
from lessons.tests.helpers import HandleGroups


class SchoolTermStudentView(TestCase):
    """Unit tests of the school term student view"""

    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
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

    def test_get_transaction_admin_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_term_view.html')
        terms = response.context['terms']
        self.assertTrue(isinstance(terms, QuerySet))

    def test_school_terms_student_view_displays_all_terms(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_term_view.html')
        terms = response.context['terms']
        self.assertEqual(terms.all().count(), SchoolTerm.objects.count())
