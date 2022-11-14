from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import User, BankTransaction
import datetime

class TransactionModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email = 'user1@test.com',
            password = 'pass1'
        )
        self.user2 = User.objects.create_user(
            email = 'user2@test.com',
            password = 'pass2'
        )
        
        self.transaction1 = BankTransaction.objects.create(
            student = self.user1,
            amount = '3.14',
            invoice_number = '1234-567',
            date = datetime.date(2022, 2, 21)
        )
        self.transaction2 = BankTransaction.objects.create(
            student = self.user2,
            amount = '3.15',
            invoice_number = '1234-569',
            date = datetime.date(2022, 2, 22)
        )

    def _assert_transaction_is_valid(self):
        try:
            self.transaction1.full_clean()
        except (ValidationError):
            self.fail('Test transaction should be valid.')
    
    def _assert_transaction_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.transaction1.full_clean()

    def test_valid_transaction(self):
        self._assert_transaction_is_valid()

    def test_date_must_not_be_blank(self):
        self.transaction1.date = None
        self._assert_transaction_is_invalid()

    def test_date_cannot_be_in_future(self):
        self.transaction1.date = datetime.date(2030, 1, 1)
        self._assert_transaction_is_invalid()

    def test_date_can_be_today(self):
        self.transaction1.date = datetime.date.today()
        self._assert_transaction_is_valid()

    def test_date_may_be_shared(self):
        self.transaction1.date = self.transaction2.date
        self._assert_transaction_is_valid()

    def test_user_must_exist(self):
        self.transaction1.student.delete()
        self._assert_transaction_is_invalid()

    def test_user_must_not_be_blank(self):
        self.transaction1.student = None
        self._assert_transaction_is_invalid()

    def test_amount_must_not_contain_over_2_decimal(self):
        self.transaction1.amount = '3.142'
        self._assert_transaction_is_invalid()
    
    def test_amount_must_not_contain_over_6_digits(self):
        self.transaction1.amount = '31989.59'
        self._assert_transaction_is_invalid()

    def test_amount_must_not_be_blank(self):
        self.transaction1.amount = None
        self._assert_transaction_is_invalid()

    def test_invoice_no_must_not_be_over_eight_characters(self):
        self.transaction1.invoice_number = '1234-1234'
        self._assert_transaction_is_invalid()

    def test_invoice_no_must_be_unique(self):
        self.transaction1.invoice_number = self.transaction2.invoice_number
        self._assert_transaction_is_invalid()

    def test_invoice_no_must_not_be_blank(self):
        self.transaction1.invoice_number = ''
        self._assert_transaction_is_invalid()

    def test_invoice_no_must_follow_format(self):
        self.transaction1.invoice_number = '12-34567'
        self._assert_transaction_is_invalid()
