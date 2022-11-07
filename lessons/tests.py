from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import User, Request

class RequestModelTestCase(TestCase):
    def setUp(self):
        self.request = Request.objects.create(
            user = User.objects.create_user(
                username='username',
                password='password'
            ),
            number_of_lessons = 1,
            interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES,
            further_information = 'Some information...'
        )
        self.request.availability.create(day = Request.Day.MONDAY)
        self.request.availability.create(day = Request.Day.WEDNESDAY)
        self.request.availability.create(day = Request.Day.SUNDAY)
    
    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except (ValidationError):
            self.fail('Test request should be valid.')
    
    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()
    
    def test_request_is_valid(self):
        self._assert_request_is_valid()
    
    def test_user_must_exist(self):
        self.request.user.delete()
        self._assert_request_is_invalid()

    # Not sure how to implement this restraint.
    '''
    def test_availability_must_have_at_least_one_available_day(self):
        self.request.availability.clear()
        self._assert_request_is_invalid()
    '''

    def test_availability_can_have_one_available_day(self):
        self.request.availability.clear()
        self.request.availability.create(day = Request.Day.MONDAY)
        self._assert_request_is_valid()

    def test_availability_can_have_all_available_days(self):
        self.request.availability.clear()
        self.request.availability.create(day = Request.Day.MONDAY)
        self.request.availability.create(day = Request.Day.TUESDAY)
        self.request.availability.create(day = Request.Day.WEDNESDAY)
        self.request.availability.create(day = Request.Day.THURSDAY)
        self.request.availability.create(day = Request.Day.FRIDAY)
        self.request.availability.create(day = Request.Day.SATURDAY)
        self.request.availability.create(day = Request.Day.SUNDAY)
        self._assert_request_is_valid()
    
    def test_number_of_lessons_cannot_be_below_one(self):
        self.request.number_of_lessons = 0
        self._assert_request_is_invalid()
    
    def test_further_information_cannot_be_blank(self):
        self.request.further_information = ''
        self._assert_request_is_invalid()
    
    def test_further_information_can_be_500_characters_long(self):
        self.request.further_information = 'x' * 500
        self._assert_request_is_valid()
    
    def test_further_information_cannot_be_over_500_characters_long(self):
        self.request.further_information = 'x' * 501
        self._assert_request_is_invalid()