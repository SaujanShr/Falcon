"""Unit tests of the School Term deletion confirmation view."""
import datetime
from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm
from lessons.tests.helpers import HandleGroups, reverse_with_next


class SchoolTermViewDeletionConfirmation(TestCase):
    """Unit tests of the School Term deletion confirmation view."""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()

        # Admin login
        self.client.login(email='janedoe@email.com', password='Password123')

        self.term1 = SchoolTerm.objects.create(
            term_name="TermOne",
            start_date=datetime.date(2022, 1, 1),
            end_date=datetime.date(2022, 12, 31)
        )

        self.term2 = SchoolTerm.objects.create(
            term_name="TermTwo",
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 12, 31)
        )

        self.url = reverse('term_deletion_confirmation_view')

    def test_school_term_deletion_confirmation_view_url(self):
        self.assertEqual(self.url, '/admin_term_view/delete_confirmation')

    def test_student_cannot_access_school_terms_deletion_confirmation_view(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url, follow=True)

        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_get_school_term_deletion_confirmation_redirects_when_not_logged_in(self):
        self.client.logout()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_deletion(self):
        self.form_input = {'old_term_name': 'TermOne'}
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input,follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count-1)
        response_url = reverse('admin_term_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_term_view.html')

