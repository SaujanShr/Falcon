"""Unit tests of the school term model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import SchoolTerm
import datetime


class SchoolTermModelTestCase(TestCase):
    """Unit tests of the school term model"""

    fixtures = ['lessons/tests/fixtures/default_terms.json']
    
    def setUp(self):
        self.term1 = SchoolTerm.objects.get(id=1)
        self.term2 = SchoolTerm.objects.get(id=2)

    def _assert_term1_is_valid(self):
        try:
            self.term1.full_clean()
        except ValidationError:
            self.fail('Test term should be valid')

    def _assert_term1_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.term1.full_clean()

    def _assert_term2_is_valid(self):
        try:
            self.term2.full_clean()
        except ValidationError:
            self.fail('Test term should be valid')

    def _assert_term2_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.term2.full_clean()

    def test_term_is_valid(self):
        self._assert_term1_is_valid()

    def test_start_date_cannot_be_blank(self):
        self.term1.start_date = ''
        self._assert_term1_is_invalid()

    def test_end_date_cannot_be_blank(self):
        self.term1.end_date = ''
        self._assert_term1_is_invalid()

    def test_end_date_cannot_be_before_start_date(self):
        self.term1.end_date = datetime.date(2021, 1, 1)
        self._assert_term1_is_invalid()

    def test_start_date_and_end_date_both_cannot_be_blank(self):
        self.term1.start_date = ''
        self.term1.end_date = ''
        self._assert_term1_is_invalid()

    def test_start_date_can_be_right_after_another_term(self):
        self.term2.start_date = datetime.date(2022, 12, 31)
        self.term2.start_date = datetime.date(2023, 12, 31)
        self._assert_term1_is_valid()

    def test_start_date_can_be_right_before_another_term(self):
        self.term2.start_date = datetime.date(2021, 1, 1)
        self.term2.start_date = datetime.date(2021, 12, 31)
        self._assert_term1_is_valid()

    def test_new_term_dates_can_be_before_existing_terms(self):
        self.term2.start_date = datetime.date(2021, 1, 1)
        self.term2.end_date = datetime.date(2021, 1, 2)
        self._assert_term2_is_valid()

    def test_new_term_dates_can_be_after_existing_terms(self):
        self.term2.start_date = datetime.date(2023, 1, 1)
        self.term2.end_date = datetime.date(2023, 1, 2)
        self._assert_term2_is_valid()

    def test_term_name_cannot_be_the_same(self):
        self.term2.term_name = 'Term one'
        self._assert_term2_is_invalid()

    def test_term_name_cannot_be_blank(self):
        self.term2.term_name = ''
        self._assert_term2_is_invalid()

    def test_term_name_can_be_18_characters_long(self):
        self.term1.term_name = 'a' * 18
        self.term1.start_date = datetime.date(2024, 1, 1)
        self.term1.end_date = datetime.date(2024, 1, 2)
        self._assert_term1_is_valid()

    def test_term_name_cannot_be_over_18_characters_long(self):
        self.term1.term_name = 'a' * 19
        self.term1.start_date = datetime.date(2024, 1, 1)
        self.term1.end_date = datetime.date(2024, 1, 2)
        self._assert_term1_is_invalid()


