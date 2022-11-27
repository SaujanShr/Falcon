"""Unit tests of the user form."""
from django import forms
from django.test import TestCase
from lessons.forms import UserForm
from lessons.models import User

class UserFormTestCase(TestCase):
    """Unit tests of the user form."""

    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        self.form_input = {
            'email': 'janedoe@example.org',
            'first_name': 'Jane',
            'last_name': 'Doe'
        }

    def test_form_has_necessary_fields(self):
        form = UserForm()
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

    def test_valid_user_form(self):
        form = UserForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['email'] = 'NOT_AN_EMAIL'
        form = UserForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        user = User.objects.get(email='johndoe@email.com')
        form = UserForm(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(user.email, 'janedoe@example.org')
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
