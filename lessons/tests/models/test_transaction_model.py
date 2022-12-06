from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import User, BankTransaction, Student, Invoice
from decimal import Decimal
import datetime
from lessons.tests.helpers import create_user_groups

class TransactionModelTestCase(TestCase):
    '''Unit tests for the transaction model'''

    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        create_user_groups()
        self.user1 = User.objects.get(email='johndoe@email.com')
        self.user2 = User.objects.get(email='janedoe@email.com')

        self.student1 = Student.objects.create(user=self.user1)
        self.student2 = Student.objects.create(user=self.user2)

        self.invoice1 = Invoice.objects.create(
            invoice_number='1234-123',
            student=self.student1,
            full_amount='100.00'
        )

        self.invoice2 = Invoice.objects.create(
            invoice_number='1234-124',
            student=self.student2,
            full_amount='100.00'
        )
        
        self.transaction1 = BankTransaction.objects.create(
            student = self.student1,
            amount = '50.00',
            invoice = self.invoice1,
            date = datetime.date(2022, 2, 21)
        )

        self.transaction2 = BankTransaction.objects.create(
            student = self.student2,
            amount = '55.00',
            invoice = self.invoice2,
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

    def test_invoice_must_exist(self):
        self.transaction1.invoice.delete()
        self._assert_transaction_is_invalid()

    def test_invoice_gets_updated(self):
        self.assertEqual(Decimal(self.transaction1.amount), self.transaction1.invoice.paid_amount)

    
    def test_invoice_overpay_interaction(self):
        transactionBig = BankTransaction.objects.create(
            student = self.student1,
            amount = '105.00',
            invoice = self.invoice1,
            date = datetime.date(2022, 2, 22)
        )
        self.assertEqual(transactionBig.invoice.fully_paid, True)
        self.assertEqual(transactionBig.invoice.full_amount, transactionBig.invoice.paid_amount)
    
    
    def test_user_balance_gets_updated_if_overpay(self):
        transactionBig = BankTransaction.objects.create(
            student = self.student1,
            amount = '105.00',
            invoice = self.invoice1,
            date = datetime.date(2022, 2, 22)
        )
        self.assertEqual(transactionBig.student.balance, Decimal('55.00'))
    