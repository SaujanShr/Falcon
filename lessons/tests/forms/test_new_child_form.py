"""Unit tests for the NewChildForm form"""
from django.test import TestCase
from lessons.models import User, Child
from lessons.forms import NewChildForm


class NewChildFormTestCase(TestCase):
    """Unit tests for the NewChildForm form"""
    
    fixtures = ['lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.form_input = {
            'first_name':'Alice',
            'last_name':'Doe'
        }
        self.user = User.objects.all()[0]
    
    def _assert_form_is_valid(self):
        form = NewChildForm(user=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())
        
    def _assert_form_is_invalid(self):
        form = NewChildForm(user=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_valid_new_child_form(self):
        self._assert_form_is_valid()
    
    def test_form_contains_required_fields(self):
        form = NewChildForm()
        self.assertNotIn('parent', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
    
    def test_form_rejects_blank_first_name(self):
        self.form_input['first_name'] = ''
        self._assert_form_is_invalid()
    
    def test_form_rejects_blank_last_name(self):
        self.form_input['last_name'] = ''
        self._assert_form_is_invalid()
        
    def test_form_rejects_first_name_with_over_50_characters(self):
        self.form_input['first_name'] = 'x' * 51
        self._assert_form_is_invalid()
    
    def test_form_rejects_last_name_with_over_50_characters(self):
        self.form_input['last_name'] = 'x' * 51
        self._assert_form_is_invalid()

    def test_form_accepts_first_name_with_50_characters(self):
        self.form_input['first_name'] = 'x' * 50
        self._assert_form_is_valid()
    
    def test_form_accepts_last_name_with_50_characters(self):
        self.form_input['last_name'] = 'x' * 50
        self._assert_form_is_valid()
    
    def test_form_saves_correctly(self):
        form = NewChildForm(user=self.user, data=self.form_input)
        
        before_count = Child.objects.count()
        form.save()
        after_count = Child.objects.count()
        self.assertEqual(before_count+1, after_count)
        
        child = Child.objects.all()[0]
        self.assertEqual(child.parent, self.user)
        self.assertEqual(child.first_name, 'Alice')
        self.assertEqual(child.last_name, 'Doe')