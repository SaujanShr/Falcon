from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import User, Request, DayOfTheWeek
from django.utils import timezone

'''
from lessons.models import User, Request, DayOfTheWeek
from django.utils import timezone
DayOfTheWeek.objects.create(order = 0, day = DayOfTheWeek.Day.MONDAY)
DayOfTheWeek.objects.create(order = 1, day = DayOfTheWeek.Day.TUESDAY)
DayOfTheWeek.objects.create(order = 2, day = DayOfTheWeek.Day.WEDNESDAY)
DayOfTheWeek.objects.create(order = 3, day = DayOfTheWeek.Day.THURSDAY)
DayOfTheWeek.objects.create(order = 4, day = DayOfTheWeek.Day.FRIDAY)
DayOfTheWeek.objects.create(order = 5, day = DayOfTheWeek.Day.SATURDAY)
DayOfTheWeek.objects.create(order = 6, day = DayOfTheWeek.Day.SUNDAY)
request1 = Request.objects.create(
user = User.objects.create_user(
username='username',
password='password'
),
date = timezone.datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
number_of_lessons = 1,
interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK,
duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES,
further_information = 'Some information...'
)
request1.availability.set([DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.MONDAY), DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.SUNDAY)])
'''

class RequestModelTestCase(TestCase):
    def setUp(self):
        DayOfTheWeek.objects.create(order = 0, day = DayOfTheWeek.Day.MONDAY)
        DayOfTheWeek.objects.create(order = 1, day = DayOfTheWeek.Day.TUESDAY)
        DayOfTheWeek.objects.create(order = 2, day = DayOfTheWeek.Day.WEDNESDAY)
        DayOfTheWeek.objects.create(order = 3, day = DayOfTheWeek.Day.THURSDAY)
        DayOfTheWeek.objects.create(order = 4, day = DayOfTheWeek.Day.FRIDAY)
        DayOfTheWeek.objects.create(order = 5, day = DayOfTheWeek.Day.SATURDAY)
        DayOfTheWeek.objects.create(order = 6, day = DayOfTheWeek.Day.SUNDAY)
        self.request1 = Request.objects.create(
            user = User.objects.create_user(
                email='email@email.com',
                password='password'
            ),
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
            user = User.objects.create_user(
                email='email2@email.com',
                password='password'
            ),
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
    
    def test_date_must_be_unique(self):
        self.request1.date = self.request2.date
        self._assert_request_is_invalid()
    
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

    # Not sure how to implement this restraint.
    '''
    def test_availability_must_have_at_least_one_available_day(self):
        self.request.availability.clear()
        self._assert_request_is_invalid()
    '''

    def test_availability_can_have_one_available_day(self):
        self.request1.availability.clear()
        self.request1.availability.add(DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.SATURDAY))
        self._assert_request_is_valid()
    
    def test_availability_may_be_the_same(self):
        self.request1.availability.set(self.request2.availability.all())
        self._assert_request_is_valid()


    def test_availability_can_have_all_available_days(self):
        self.request1.availability.clear()
        self.request2.availability.set([DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.MONDAY), 
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.TUESDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.WEDNESDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.THURSDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.FRIDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.SATURDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.SUNDAY)])
        self._assert_request_is_valid()
    
    def test_number_of_lessons_cannot_be_below_one(self):
        self.request1.number_of_lessons = 0
        self._assert_request_is_invalid()
    
    def test_number_of_lessons_may_be_the_same(self):
        self.request1.number_of_lessons = self.request2.number_of_lessons
        self._assert_request_is_valid()
    
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