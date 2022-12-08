"""Unit tests of the user invoice list View."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import Invoice, User, Student
from django.db.models.query import QuerySet
from lessons.tests.helpers import create_user_groups


class InvoiceStudentListTestCase(TestCase):
    """Unit tests of the user invoice list View."""

    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        create_user_groups()
        self.john_doe_user = User.objects.get(email='johndoe@email.com')
        self.jane_doe_user = User.objects.get(email='janedoe@email.com')
        self.url = reverse('invoice_list_student')
        self.student = Student.objects.create(user = self.john_doe_user)
        self.student2 = Student.objects.create(user = self.jane_doe_user)
        self.superuser = User.objects.create_superuser(
            email='admin@email.com',
            password='password'
        )
        self.invoice1 = Invoice.objects.create(
            invoice_number = '1234-123',
            student=self.student,
            full_amount='100.00'
        )
        self.invoice2 = Invoice.objects.create(
            invoice_number = '1234-124',
            student=self.student2,
            full_amount='100.00'
        )

    def test_invoice_student_url(self):
        self.assertEqual(self.url, '/invoice/student')

    def test_get_invoice_student_view(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_list.html')
        invoices = response.context['invoices']
        self.assertTrue(isinstance(invoices, QuerySet))

    def test_invoice_view_displays_only_users_invoices(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_list.html')
        invoices = response.context['invoices']
        self.assertEqual(invoices.all().count(), Invoice.objects.filter(student=self.student).count())