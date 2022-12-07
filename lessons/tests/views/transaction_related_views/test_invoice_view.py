from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Student, Invoice
from lessons.tests.helpers import create_user_groups
from lessons.forms import InvoiceEditForm
from decimal import Decimal

class InvoiceViewTestCase(TestCase):
    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']

    def setUp(self):
        create_user_groups()
        self.user1 = User.objects.get(email='johndoe@email.com')
        self.user2 = User.objects.get(email='janedoe@email.com')
        self.url = reverse('invoice_view')

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

        self.client.login(email="johndoe@email.com", password="Password123")

    def test_invoice_view_url(self):
        self.assertEqual(self.url, '/invoice/view')

    def test_get_valid_invoice_view(self):
        response = self.client.get(self.url, {'invoice_id': self.invoice1.invoice_number})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_view.html')

    def test_get_invalid_invoice_view(self):
        response = self.client.get(self.url, {'invoice_id': '0000-000'}, follow=True)
        response_url = reverse('invoice_list_student')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200) 

    def test_invoice_view_form(self):
        response = self.client.get(self.url, {'invoice_id': self.invoice1.invoice_number})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, InvoiceEditForm))

    def test_invoice_form_in_view_contains_necessary_fields(self):
        response = self.client.get(self.url, {'invoice_id': self.invoice1.invoice_number})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_view.html')
        form = response.context['form']
        self.assertIn('invoice_number', form.fields)
        self.assertIn('student_name', form.fields)
        self.assertIn('full_amount', form.fields)
        self.assertIn('paid_amount', form.fields)

    def test_invoice_form_in_view_contains_correct_info(self):
        response = self.client.get(self.url, {'invoice_id': self.invoice1.invoice_number})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_view.html')
        form = response.context['form']
        self.assertEqual(form.initial['invoice_number'], self.invoice1.invoice_number)
        self.assertEqual(form.initial['student_name'], self.invoice1.student.user.email)
        self.assertEqual(Decimal(form.initial['full_amount']), Decimal(self.invoice1.full_amount))
        self.assertEqual(Decimal(form.initial['paid_amount']), Decimal(self.invoice1.paid_amount))


    def test_invoice_form_fields_are_disabled_in_view(self):
        response = self.client.get(self.url, {'invoice_id': self.invoice1.invoice_number})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice_view.html')
        form = response.context['form']
        self.assertTrue(form.fields['invoice_number'].disabled)
        self.assertTrue(form.fields['student_name'].disabled)
        self.assertTrue(form.fields['full_amount'].disabled)
        self.assertTrue(form.fields['paid_amount'].disabled)

    def test_unauthorised_user_cannot_see_invoice(self):
        self.client.logout()
        self.client.login(email="janedoe@email.com", password="Password123")
        response = self.client.get(self.url, {'invoice_id': self.invoice1.invoice_number}, follow=True)
        response_url = reverse('invoice_list_student')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200) 

    def test_return_button_redirects(self):
        response_url = reverse('invoice_list_student')
        response = self.client.post(self.url, {'invoice_id': self.invoice1.invoice_number}, follow=True)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200) 
