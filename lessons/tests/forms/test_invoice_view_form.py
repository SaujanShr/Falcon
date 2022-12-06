from django.test import TestCase
from lessons.models import User, Booking, Invoice
from lessons.forms import InvoiceViewForm

class InvoiceViewFormTestCase(TestCase):
    '''Unit tests for the InvoiceViewForm form'''
    
    fixtures = ['lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.user = User.objects.get(email='johndoe@email.com')
        self.form = InvoiceViewForm(
            initial={
                'invoice_number':'0001-0001',
                'student_name': 'John Doe',
                'full_amount': 999.9,
                'paid_amount': 990.0,
                'fully_paid': False
            }
        )
    
    def test_form_has_necessary_fields(self):
        self.assertIn('invoice_number', self.form.fields)
        self.assertIn('student_name', self.form.fields)
        self.assertIn('full_amount', self.form.fields)
        self.assertIn('paid_amount', self.form.fields)
        self.assertIn('fully_paid', self.form.fields)
        
    def test_form_fields_are_disabled(self):
        fields = self.form.fields
        self.assertTrue(fields['invoice_number'].disabled)
        self.assertTrue(fields['student_name'].disabled)
        self.assertTrue(fields['full_amount'].disabled)
        self.assertTrue(fields['paid_amount'].disabled)
        self.assertTrue(fields['fully_paid'].disabled)
    
    def test_form_fields_have_correct_initial_values(self):
        self.assertEqual(self.form['invoice_number'].value(), '0001-0001')
        self.assertEqual(self.form['student_name'].value(), 'John Doe')
        self.assertEqual(self.form['full_amount'].value(), 999.9)
        self.assertEqual(self.form['paid_amount'].value(), 990.0)
        self.assertEqual(self.form['fully_paid'].value(), False)
        
    def test_form_cannot_save(self):
        self.assertFalse(self.form.is_valid())