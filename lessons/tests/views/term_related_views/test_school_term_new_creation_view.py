"""Unit tests of the School Term creation view."""
import datetime
from django.test import TestCase
from django import forms
from django.urls import reverse
from django.contrib import messages
from lessons.forms import TermEditForm
from lessons.models import SchoolTerm
from lessons.tests.helpers import HandleGroups, reverse_with_next


class NewSchoolTermView(TestCase):
    """Unit tests of the School Term creation view."""
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

        self.form_input = {
            'term_name': 'TermThree',
            'start_date': datetime.date(2024, 1, 1),
            'end_date': datetime.date(2024, 12, 31),
        }

        self.url = reverse('new_term_view')

    def test_new_school_term_view_url(self):
        self.assertEqual(self.url, '/admin_term_view/new_term')

    def test_form_has_required_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_term_view.html')

        form = response.context['form']

        self.assertIn('term_name', form.fields)

        self.assertIn('start_date', form.fields)
        start_date_field = form.fields['start_date']
        self.assertTrue(isinstance(start_date_field, forms.DateField))

        self.assertIn('end_date', form.fields)
        end_date_field = form.fields['end_date']
        self.assertTrue(isinstance(end_date_field, forms.DateField))

    def test_student_cannot_access_school_terms_admin_edit_view(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url, follow=True)

        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_get_new_school_term_redirects_when_not_logged_in(self):
        self.client.logout()
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_unsuccessful_term_creation_due_to_invalid_start_date(self):
        self.form_input['start_date'] = 'NOT_A_DATE'
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_term_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermEditForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_term_creation_due_to_invalid_end_date(self):
        self.form_input['end_date'] = 'NOT_A_DATE'
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_term_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermEditForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_term_creation_due_end_date_before_start_date(self):
        self.form_input['start_date'] = datetime.date(2024, 12, 31)
        self.form_input['end'] = datetime.date(2024, 1, 1)
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_term_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermEditForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_term_creation_due_to_duplicate_name(self):
        self.form_input['term_name'] = 'TermOne'
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_term_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermEditForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_term_creation_due_to_empty_name(self):
        self.form_input['term_name'] = ''
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_term_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermEditForm))
        self.assertTrue(form.is_bound)

    def test_unsuccessful_term_creation_due_to_new_date_clashes_with_existing_term(self):
        self.form_input['start_date'] = datetime.date(2022, 1, 2)
        self.form_input['end'] = datetime.date(2022, 1, 3)
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_term_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TermEditForm))
        self.assertTrue(form.is_bound)

    def test_successful_term_creation(self):
        before_count = SchoolTerm.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('admin_term_view')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_term_view.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        term = SchoolTerm.objects.get(term_name="TermThree")
        self.assertEqual(term.term_name, 'TermThree')
        self.assertEqual(term.start_date, datetime.date(2024, 1, 1))
        self.assertEqual(term.end_date, datetime.date(2024, 12, 31))
