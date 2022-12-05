from django.test import TestCase
from sqlite3 import IntegrityError
from django.core.exceptions import ValidationError
from lessons.models import Invoice, User, Student
from lessons.tests.helpers import create_user_groups

class InvoiceModelTestCase(TestCase):

    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']
    #Do we need to import other user?


    def setUp(self):
        create_user_groups()

        self.student1 = Student.objects.create(
            user=User.objects.get(email="johndoe@email.com"),
            balance=100
        )

        self.invoice1 = Invoice.objects.create(
            invoice_number="0001-001",
            student=self.student1,
            full_amount=1000,
            paid_amount=0,
            fully_paid=False
        )

        self.invoice2 = Invoice.objects.create(
            invoice_number="0001-002",
            student=self.student1,
            full_amount=1000,
            paid_amount=0,
            fully_paid=False
        )

    def _assert_invoice_is_valid(self):
        try:
            self.invoice1.full_clean()
        except (ValidationError):
            self.fail('Test request should be valid.')


    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice1.full_clean()


    def test_invoice_is_valid(self):
        self._assert_invoice_is_valid()

    def test_invoice_number_cannot_be_blank(self):
        self.invoice1.invoice_number = ''
        self._assert_invoice_is_invalid()

    def test_invoice_number_cannot_follow_invalid_format(self):
        self.invoice1.invoice_number = '002-0001'
        self._assert_invoice_is_invalid()

    def test_amount_paid_cannot_be_higher_than_full_amount(self):
        self.invoice1.paid_amount = 1001
        self._assert_invoice_is_invalid()

    def test_amount_paid_can_be_equal_to_full_amount(self):
        self.invoice1.paid_amount = 1000
        self.invoice1.fully_paid = True
        self._assert_invoice_is_valid()

    def test_fully_paid_cant_be_false_if_paid_amount_equals_full_amount(self):
        self.invoice1.paid_amount = 1000
        self._assert_invoice_is_invalid()

    def test_student_must_exist(self):
        self.invoice1.student.delete()
        self._assert_invoice_is_invalid()

    def test_paid_amount_cannot_be_negative(self):
        self.invoice1.paid_amount = -1
        self._assert_invoice_is_invalid()

    def test_full_amount_cannot_be_negative(self):
        self.invoice1.full_amount = -1
        self._assert_invoice_is_invalid()

    def test_fully_paid_cannot_be_true_if_paid_amount_not_equal_to_full_amount(self):
        self.invoice1.fully_paid = True
        self._assert_invoice_is_invalid()
