"""Unit test for the Child model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import User, Child


class ChildModelTestCase(TestCase):
    """Unit test for the Child model"""
    
    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.user1 = User.objects.all()[0]
        self.user2 = User.objects.all()[1]

        self.child1 = Child.objects.create(
            parent=self.user1,
            first_name='Alice',
            last_name='Doe'
        )
        self.child2 = Child.objects.create(
            parent=self.user2,
            first_name='Bob',
            last_name='Doe'
        )
        
    def _assert_child_is_valid(self):
        try:
            self.child1.full_clean()
        except ValidationError:
            self.fail('Test child should be valid.')
    
    def _assert_child_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.child1.full_clean()
    
    def test_child_is_valid(self):
        self._assert_child_is_valid()
        
    def test_child_must_have_a_parent(self):
        self.child1.parent = None
        self._assert_child_is_invalid()
    
    def test_children_can_have_the_same_parent(self):
        self.child1.parent = self.child2.parent
        self._assert_child_is_valid()
    
    def test_children_can_have_the_same_name_different_parents(self):
        self.child1.first_name = self.child2.last_name
        self.child1.last_name = self.child2.last_name
        self._assert_child_is_valid()
    
    def test_children_can_have_the_same_name_same_parent(self):
        self.child1.parent = self.child2.parent
        self.child1.first_name = self.child2.last_name
        self.child1.last_name = self.child2.last_name
        self._assert_child_is_valid()
    
    def test_first_name_cannot_contain_above_50_characters(self):
        self.child1.first_name = 'x' * 51
        self._assert_child_is_invalid()
    
    def test_first_name_may_contain_50_characters(self):
        self.child1.first_name = 'x' * 50
        self._assert_child_is_valid()

    def test_first_name_cannot_be_blank(self):
        self.child1.first_name = ''
        self._assert_child_is_invalid()
    
    def test_last_name_cannot_contain_above_50_characters(self):
        self.child1.last_name = 'x' * 51
        self._assert_child_is_invalid()
    
    def test_last_name_may_contain_50_characters(self):
        self.child1.last_name = 'x' * 50
        self._assert_child_is_valid()

    def test_last_name_cannot_be_blank(self):
        self.child1.last_name = ''
        self._assert_child_is_invalid()