"""Tests of the admin page to see all bookings and requests."""
from django.test import TestCase
from ..models import User, Request, DayOfTheWeek
from django.utils import timezone
class AdminRequestsViewTestCase(TestCase):
    """Tests of the admin page to see all bookings and requests."""

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
                username='username',
                password='password'
            ),
            date = timezone.now(),
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
                username='username2',
                password='password'
            ),
            date = timezone.now(),
            number_of_lessons = 2,
            interval_between_lessons = Request.IntervalBetweenLessons.TWO_WEEKS,
            duration_of_lessons = Request.LessonDuration.SIXTY_MINUTES,
            further_information = 'Other information'
        )
        self.request2.availability.set([DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.TUESDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.THURSDAY),
                                        DayOfTheWeek.objects.get(day = DayOfTheWeek.Day.FRIDAY)])
    def test_get_admin_request_view_page(self):
        url = '/'
