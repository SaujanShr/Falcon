from django.test import TestCase
from lessons.forms import RequestForm
from lessons.tests.helpers import create_days_of_the_week

class RequestViewFormTestCase(TestCase):
    def setUp(self):
        create_days_of_the_week()
        