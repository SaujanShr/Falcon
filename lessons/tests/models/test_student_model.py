""""Unit test for the Student model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User,Student


class StudentModelTestCase(TestCase):
    """"Unit test for the Student model"""

    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.johndoe = User.objects.get(email='johndoe@email.com')
        self.janedoe = User.objects.get(email='janedoe@email.com')
        self.student1 = Student.objects.create(user = self.johndoe)
        self.student2 = Student.objects.create(user = self.janedoe, balance=1000)

    def _assert_student2_is_valid(self):
        try:
            self.student2.full_clean()
        except (ValidationError):
            self.fail('Test student should be valid.')
    
    def _assert_student2_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student2.full_clean()

    def test_valid_student(self):
        self._assert_student2_is_valid()
    
    def test_balance_defaults_to_0(self):
        self.assertEqual(self.student1.balance,0)
    
    def test_user_cannot_be_blank(self):
        self.student2.user = None
        self._assert_student2_is_invalid()

    def test_student_is_linked_to_right_user(self):
        self.assertEqual(self.student2.user,self.janedoe)

    def test_student_is_not_linked_to_wrong_user(self):
        self.assertNotEqual(self.student2.user,self.johndoe)
    
    def test_can_get_student_from_user(self):
        student = Student.objects.get(user=self.johndoe)
        self.assertEqual(student,self.student1)
        self.assertEqual(student.user.email,self.johndoe.email)
        self.assertEqual(student.balance,self.student1.balance)
