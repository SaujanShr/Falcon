"""Unit tests of the School Term deletion confirmation view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import SchoolTerm
from lessons.tests.helpers import HandleGroups, reverse_with_next


class SchoolTermViewDeletionConfirmation(TestCase):
    """Unit tests of the School Term deletion confirmation view."""
    fixtures = [
        'lessons/tests/fixtures/default_user.json',
        'lessons/tests/fixtures/other_users.json',
        'lessons/tests/fixtures/default_terms.json'
    ]

    def setUp(self):
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()

        # Admin login
        self.client.login(email='janedoe@email.com', password='Password123')

        self.term1 = SchoolTerm.objects.get(id=1)
        self.term2 = SchoolTerm.objects.get(id=2)

        self.url = reverse('term_deletion_confirmation_view')

    def test_school_term_deletion_confirmation_view_url(self):
        self.assertEqual(self.url, '/admin_term_view/delete_confirmation')

    def test_student_cannot_access_school_terms_deletion_confirmation_view(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url, follow=True)

        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_get_school_term_deletion_confirmation(self):
        self.form_input = {'term_name': 'TermOne'}
        response = self.client.get(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'term_deletion_confirmation.html')

    def test_get_school_term_deletion_confirmation_redirects_without_term_name(self):
        self.form_input = ''
        response = self.client.get(self.url, self.form_input, follow=True)
        redirect_url = reverse('admin_term_view')
        self.assertRedirects(response, redirect_url,
                             status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_term_view.html')

    def test_get_school_term_deletion_confirmation_redirects_when_not_logged_in(self):
        self.client.logout()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_successful_deletion(self):
        self.form_input = {'term_name': 'TermOne'}
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count-1)
        response_url = reverse('admin_term_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_term_view.html')

    def test_unsuccessful_deletion_due_to_non_existent_term_name(self):
        self.form_input = {'term_name': 'NOT_A_TERM'}
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('admin_term_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_term_view.html')
