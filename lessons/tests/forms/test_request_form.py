from django.test import TestCase
from lessons.forms import RequestViewForm
from lessons.tests.helpers import create_days_of_the_week

class RequestFormTestCase(TestCase):
    def setUp(self):
        create_days_of_the_week()
        