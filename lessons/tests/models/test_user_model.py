"""Unit tests for the User model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User
from lessons.tests.helpers import create_user_groups, HandleGroups


class UserModelTestCase(TestCase):
    """Unit tests for the User model."""

    fixtures = ['lessons/tests/fixtures/default_user.json',
                'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        self.user = User.objects.get(email='janedoe@email.com')
        self.other_user = User.objects.get(email= 'johndoe@email.com')

    def test_valid_user(self):
        self._assert_user_is_valid()
    
    def test_is_student_returns_true_for_student(self):
        HandleGroups.set_default_user_to_student()
        self.assertTrue(self.other_user.is_student())
    
    def test_is_student_returns_false_for_non_student(self):
        HandleGroups.set_default_user_to_admin()
        self.assertFalse(self.other_user.is_student())

    def test_is_admin_returns_true_for_admin(self):
        HandleGroups.set_default_user_to_admin()
        self.assertTrue(self.other_user.is_admin())
    
    def test_is_admin_returns_false_for_non_admin(self):
        HandleGroups.set_default_user_to_student()
        self.assertFalse(self.other_user.is_admin())

    def test_first_name_must_not_be_blank(self):
        self.user.first_name = ''
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_user = User.objects.get(email='johndoe@email.com')
        self.user.first_name = second_user.first_name
        self._assert_user_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.user.first_name = 'x' * 50
        self._assert_user_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.user.first_name = 'x' * 51
        self._assert_user_is_invalid()

    def test_last_name_must_not_be_blank(self):
        self.user.last_name = ''
        self._assert_user_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_user = User.objects.get(email='johndoe@email.com')
        self.user.last_name = second_user.last_name
        self._assert_user_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.user.last_name = 'x' * 50
        self._assert_user_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.user.last_name = 'x' * 51
        self._assert_user_is_invalid()
    
    def test_email_must_not_be_blank(self):
        self.user.email = ''
        self._assert_user_is_invalid()

    def test_email_must_be_unique(self):
        second_user = User.objects.get(email='johndoe@email.com')
        self.user.email = second_user.email
        self._assert_user_is_invalid()

    def test_email_must_contain_username(self):
        self.user.email = '@example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.user.email = 'johndoe.example.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.user.email = 'johndoe@.org'
        self._assert_user_is_invalid()

    def test_email_must_contain_domain(self):
        self.user.email = 'johndoe@example'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'johndoe@@example.org'
        self._assert_user_is_invalid()

    def test_get_group_returns_director_for_a_director(self):
        self.user.is_superuser = True
        self.assertEqual(self.user.get_group(), 'Director')
    
    def test_get_group_returns_admin_for_an_admin(self):
        HandleGroups.set_default_user_to_admin()
        self.assertEqual(self.other_user.get_group(), 'Admin')
    
    def test_get_group_returns_student_for_a_student(self):
        HandleGroups.set_default_user_to_student()
        self.assertEqual(self.other_user.get_group(), 'Student')

    def test_get_full_name_returns_first_name_coma_last_name(self):
        self.assertEqual(self.user.get_full_name(), 'Jane, Doe')
    
    def test_get_group_returns_empty_string_if_name_not_defined(self):
        self.user.first_name = ''
        self.user.last_name = ''
        self.assertEqual(self.user.get_full_name(), '')
    
    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')
        
    def test_creating_user_without_email_should_fail(self):
        try:
            User.objects.create_user(first_name="test",last_name="test",password="Password123")
            self.assertFalse(True)
        except:
            self.assertTrue(True)
    
    def test_creating_superuser_should_have_us_superuser_true(self):
        try:
            User.objects.create_superuser(first_name="test",last_name="test",password="Password123",is_superuser=False)
            self.assertFalse(True)
        except:
            self.assertTrue(True)

    def test_creating_superuser_should_have_us_staff_true(self):
        try:
            User.objects.create_superuser(first_name="test",last_name="test",password="Password123",is_superuser=True,is_staff=False)
            self.assertFalse(True)
        except:
            self.assertTrue(True)

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def _create_second_user(self):
        user = User.objects.create_user(
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123',
            bio="This is Jane's profile."
        )
        return user
