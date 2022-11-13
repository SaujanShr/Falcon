"""Unit tests of the sign-up form."""
from django import forms
from django.test import TestCase
from lessons.forms import SignUpForm
from lessons.models import User
from django.contrib.auth.hashers import check_password


class SignUpFormTestCase(TestCase):
    """Unit tests of the sign-up form."""

    def setUp(self):
        self.form_input = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }

    def test_valid_sign_up_form(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = SignUpForm()
        self.assertIn('first_name', form.fields)

        self.assertIn('last_name', form.fields)

        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))

        self.assertIn('new_password', form.fields)

        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))

        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_first_name_uses_model_validation(self):
        self.form_input['first_name'] = 'a' * 51
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_last_name_uses_model_validation(self):
        self.form_input['last_name'] = 'a' * 51
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # New password has correct format
    def test_password_must_contain_uppercase_character(self):
        self.form_input[
            'new_password'] = 'password123'  # This input meets all other requirements for a password except uppercase characters.
        self.form_input['password_confirmation'] = 'password123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # New password and password confirmation must be identical
    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # def test_form_must_save_correctly(self):
    #     form = SignUpForm(data=self.form_input)
    #     before_count = User.objects.count()
    #     form.save()
    #     after_count = User.objects.count()
    #     self.assertEqual(after_count, before_count + 1)  # Check that the user count has increased by 1
    #
    #     user = User.objects.get(email='johndoe@example.org')
    #     self.assertEqual(user.first_name, 'John')
    #     self.assertEqual(user.last_name, 'Doe')
    #     self.assertEqual(user.email, 'johndoe@example.org')
    #     is_password_correct = check_password('Password123',
    #                                          user.password)  # Uses check_password as the password stored is a hash, using this will allow us to compare whether the given password is the same as the one stored as a hash.
    #     self.assertTrue(is_password_correct)
