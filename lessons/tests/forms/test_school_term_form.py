"""Unit tests of the School Term view form."""
import datetime
from django import forms
from django.test import TestCase
from lessons.forms import TermEditForm
from lessons.models import SchoolTerm


class SignUpFormTestCase(TestCase):
    """Unit tests of the School Term view form."""

    def setUp(self):
        self.form_input = {
            'term_name': 'Term one',
            'start_date': datetime.date(2022, 1, 1),
            'end_date': datetime.date(2022, 12, 31)
        }

    def test_valid_term_view_form(self):
        form = TermEditForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = TermEditForm()
        self.assertIn('term_name', form.fields)

        self.assertIn('start_date', form.fields)
        start_date_field = form.fields['start_date']
        self.assertTrue(isinstance(start_date_field, forms.DateField))

        self.assertIn('end_date', form.fields)
        end_date_field = form.fields['end_date']
        self.assertTrue(isinstance(end_date_field, forms.DateField))

    def test_term_name_uses_model_validation(self):
        self.form_input['term_name'] = 'a' * 18
        form = TermEditForm(data=self.form_input)
        self.assertTrue(form.is_valid())

        self.form_input['term_name'] = 'a' * 19
        form = TermEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_uses_model_validation(self):
        self.form_input['start_date'] = ''
        form = TermEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input['start_date'] = 'NOT_DATE'
        form = TermEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input['start_date'] = datetime.date(2022, 1, 1)
        form = TermEditForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_end_date_uses_model_validation(self):
        self.form_input['end_date'] = ''
        form = TermEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input['end_date'] = 'NOT_DATE'
        form = TermEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input['end_date'] = datetime.date(2024, 1, 1)
        form = TermEditForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_start_date_must_be_before_end_date(self):
        self.form_input['start_date'] = datetime.date(2022, 1, 1)
        self.form_input['end_date'] = datetime.date(2021, 1, 1)
        form = TermEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

        self.form_input['start_date'] = datetime.date(2022, 1, 1)
        self.form_input['end_date'] = datetime.date(2022, 1, 1)
        form = TermEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = TermEditForm(data=self.form_input)

        before_count = SchoolTerm.objects.count()
        form.save()
        after_count = SchoolTerm.objects.count()
        self.assertEqual(after_count, before_count + 1)  # Check that the user count has increased by 1

        term = SchoolTerm.objects.get(term_name='Term one')
        self.assertEqual(term.term_name, 'Term one')
        self.assertEqual(term.start_date, datetime.date(2022, 1, 1))
        self.assertEqual(term.end_date, datetime.date(2022, 12, 31))
