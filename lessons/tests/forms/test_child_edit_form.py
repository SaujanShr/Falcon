from django.test import TestCase
from lessons.models import User, Child
from lessons.forms import ChildEditForm

class ChildViewFormTestCase(TestCase):
    '''Unit tests for the ChildViewForm form'''
    
    fixtures = ['lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.user = User.objects.all()[0]
        
        self.child = Child.objects.create(
            parent=self.user,
            first_name='Alice',
            last_name='Doe'
        )
        
        self.form_input = {
            'first_name':'Joe',
            'last_name':'Doe'
        }
    
    def _assert_form_is_valid(self):
        form = ChildEditForm(instance_id=self.child.id, data=self.form_input)
        self.assertTrue(form.is_valid())
        
    def _assert_form_is_invalid(self):
        form = ChildEditForm(instance_id=self.child.id, data=self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_valid_child_view_form(self):
        self._assert_form_is_valid()
        
    def test_form_contains_required_fields(self):
        form = ChildEditForm(instance_id=self.child.id, data=self.form_input)
        self.assertNotIn('parent', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
    
    def test_form_fields_have_correct_initial_values(self):
        form = ChildEditForm(
            initial={
                'first_name':self.child.first_name,
                'last_name':self.child.last_name
            }
        )
        self.assertEqual(form['first_name'].value(), 'Alice')
        self.assertEqual(form['last_name'].value(), 'Doe')
    
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
    
    def test_form_accepts_the_old_first_name(self):
        self.form_input['first_name'] = self.child.first_name
        self._assert_form_is_valid()
    
    def test_form_accepts_a_new_first_name(self):
        self.form_input['first_name'] = self.child.first_name + 'x'
        self._assert_form_is_valid()
    
    def test_form_accepts_the_old_last_name(self):
        self.form_input['last_name'] = self.child.last_name
        self._assert_form_is_valid()
        
    def test_form_accepts_a_new_last_name(self):
        self.form_input['last_name'] = self.child.last_name + 'x'
        self._assert_form_is_valid()

    def test_form_saves_correctly(self):
        form = ChildEditForm(instance_id=self.child.id, data=self.form_input)
        
        before_count = Child.objects.count()
        form.save()
        after_count = Child.objects.count()
        self.assertEqual(before_count, after_count)
        
        child = Child.objects.all()[0]
        self.assertEqual(child.parent, self.user)
        self.assertEqual(child.first_name, 'Joe')
        self.assertEqual(child.last_name, 'Doe')