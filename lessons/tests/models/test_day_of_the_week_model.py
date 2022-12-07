"""Unit tests for the DayOfTheWeek model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import DayOfTheWeek
from lessons.tests.helpers import create_days_of_the_week


class DayOfTheWeekModelTestCase(TestCase):
    """Unit tests for the DayOfTheWeek model"""
    
    def setUp(self):
        create_days_of_the_week()
        DayOfTheWeek.objects.get(day='Monday').delete()
        self.day = DayOfTheWeek(order=1, day='Monday')
    
    def _assert_day_is_valid(self):
        try:
            self.day.full_clean()
        except ValidationError:
            self.fail('Test day should be valid.')

    def _assert_day_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.day.full_clean()
    
    def test_day_is_valid(self):
        self._assert_day_is_valid()

    def test_7_days_are_created(self):
        self.day.save()
        self.assertEqual(DayOfTheWeek.objects.count(), 7)
    
    def test_2_days_cannot_be_the_same(self):
        self.day = DayOfTheWeek(order=8, day="Monday")
        self._assert_day_is_invalid()
        
    def test_order_cannot_be_below_zero(self):
        self.day.order = -1
        self._assert_day_is_invalid()
        
    def test_order_can_be_zero(self):
        self.day.order = 0
        self._assert_day_is_valid()
    
    def test_order_cannot_be_above_six(self):
        self.day.order = 7
        self._assert_day_is_invalid()
    
    def test_order_can_be_six(self):
        self.day.order = 6
        self._assert_day_is_valid()

    def test_cannot_create_duplicate_day_of_the_week(self):
        self.day = DayOfTheWeek(order=1, day=DayOfTheWeek.Day.TUESDAY)
        self._assert_day_is_invalid()