from django.test import TestCase
from django.urls import reverse
from lessons.models import BankTransaction, User, Student, Invoice
from django.db.models.query import QuerySet
import datetime

class TransactionAdminListTestCase(TestCase):
    def setUp(self):
        self.url = reverse('transaction_list_admin')

        self.superuser = User.objects.create_superuser(
            email='admin@email.com',
            password='password'
        )

        self.user1 = User.objects.create_user(
                email='email1@email.com',
                password='password'
            )

        self.user2 = User.objects.create_user(
                email='email2@email.com',
                password='password'
            )

        self.student1 = Student.objects.create(user = self.user1)
        self.student2 = Student.objects.create(user = self.user2)

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
            amount = '50.00',
            invoice = self.invoice2,
            date = datetime.date(2022, 2, 21)
        )


    def test_transaction_admin_url(self):
        self.assertEqual(self.url, '/transactions/admin/view')

    def test_get_transaction_admin_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_list.html')
        transactions = response.context['transactions']
        self.assertTrue(isinstance(transactions, QuerySet))

    #TODO more tests for the transaction list view

    def test_transaction_admin_displays_all_transactions(self):
        self.client.login(email='admin@email.com', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_list.html')
        transactions = response.context['transactions']
        self.assertEqual(transactions.all().count(), BankTransaction.objects.count())