"""Unit tests of the request model"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import User, Request, DayOfTheWeek
from django.utils import timezone
from lessons.tests.helpers import create_days_of_the_week
from lessons.tests.helpers import create_user_groups
class RequestModelTestCase(TestCase):
    """Unit tests of the request model"""
    
    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        create_user_groups()
        create_days_of_the_week()

        self.request1 = Request.objects.create(
            user = User.objects.get(email='johndoe@email.com'),
            relation_id=0,
            date = timezone.datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
            number_of_lessons = 1,
            interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES,
            further_information = 'Some information...'
        )
        self.request1.availability.set([DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.MONDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.WEDNESDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.SUNDAY)])

        self.request2 = Request.objects.create(
            user = User.objects.get(email='janedoe@email.com'),
            relation_id=0,
            date = timezone.datetime(2001, 2, 2, 2, 2, 2, tzinfo=timezone.utc),
            number_of_lessons = 2,
            interval_between_lessons = Request.IntervalBetweenLessons.TWO_WEEKS,
            duration_of_lessons = Request.LessonDuration.SIXTY_MINUTES,
            further_information = 'Other information'
        )
        self.request2.availability.set([DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.TUESDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.THURSDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.FRIDAY)])
    
    def _assert_request_is_valid(self):
        try:
            self.request1.full_clean()
        except (ValidationError):
            self.fail('Test request should be valid.')
    
    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request1.full_clean()
    
    def test_request_is_valid(self):
        self._assert_request_is_valid()
    
    def test_date_cannot_be_blank(self):
        self.request1.date = ''
        self._assert_request_is_invalid()
    
    def test_date_can_already_exist(self):
        self.request1.date = self.request2.date
        self._assert_request_is_valid()
    
    def test_date_can_be_today(self):
        self.request1.date = timezone.datetime.now(tz=timezone.utc)
        self._assert_request_is_valid()
    
    def test_date_cannot_be_in_the_future(self):
        self.request1.date = timezone.datetime(9999, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
        self._assert_request_is_invalid()
    
    def test_user_must_exist(self):
        self.request1.user.delete()
        self._assert_request_is_invalid()
    
    def test_user_may_already_be_used(self):
        self.request1.user = self.request2.user
        self._assert_request_is_valid()

    def test_availability_can_have_one_available_day(self):
        self.request1.availability.clear()
        self.request1.availability.add(DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.SATURDAY))
        self._assert_request_is_valid()

    def test_availability_can_have_more_than_one_available_day(self):
        self.request1.availability.clear()
        self.request1.availability.add(DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.SATURDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.SUNDAY))
        self._assert_request_is_valid()
    
    def test_availability_may_be_the_same(self):
        self.request1.availability.set(self.request2.availability.all())
        self._assert_request_is_valid()

    def test_availability_can_have_all_available_days(self):
        self.request1.availability.clear()
        self.request2.availability.set(DayOfTheWeek.objects.all())
        self._assert_request_is_valid()

    def test_number_of_lessons_cannot_be_empty(self):
        self.request1.number_of_lessons = None
        self._assert_request_is_invalid()

    def test_number_of_lessons_cannot_be_below_one(self):
        self.request1.number_of_lessons = 0
        self._assert_request_is_invalid()
    
    def test_number_of_lessons_may_be_the_same(self):
        self.request1.number_of_lessons = self.request2.number_of_lessons
        self._assert_request_is_valid()

    def test_number_of_lessons_can_be_max_int_for_SQLite_DB(self):
        self.request1.number_of_lessons = 9223372036854775807
        self._assert_request_is_valid()

    def test_number_of_lessons_cannot_be_greater_than_max_int_for_SQLite_DB(self):
        self.request1.number_of_lessons = 92233720368547758071
        self._assert_request_is_invalid()
    
    def test_interval_between_lessons_may_be_the_same(self):
        self.request1.interval_between_lessons = self.request2.interval_between_lessons
        self._assert_request_is_valid()
    
    def test_duration_of_lessons_may_be_the_same(self):
        self.request1.duration_of_lessons = self.request2.duration_of_lessons
        self._assert_request_is_valid()
    
    def test_further_information_cannot_be_blank(self):
        self.request1.further_information = ''
        self._assert_request_is_invalid()
    
    def test_further_information_can_be_500_characters_long(self):
        self.request1.further_information = 'x' * 500
        self._assert_request_is_valid()
    
    def test_further_information_cannot_be_over_500_characters_long(self):
        self.request1.further_information = 'x' * 501
        self._assert_request_is_invalid()
    
    def test_further_information_may_be_the_same(self):
        self.request1.further_information = self.request2.further_information
        self._assert_request_is_valid()
