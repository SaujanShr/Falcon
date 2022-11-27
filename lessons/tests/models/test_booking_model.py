from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import User, DayOfTheWeek, Booking
from django.utils import timezone
from lessons.tests.helpers import create_user_groups

class BookingModelTestCase(TestCase):
    
    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        create_user_groups()
        
        self.booking1 = Booking.objects.create(
            user = User.objects.get(email="johndoe@email.com"),
            student_name="John Doe",
            invoice_id="0001-001",
            time_of_the_day="12:00",
            teacher="Mr Smith",
            number_of_lessons=20,
            start_date="2022-11-21",
            duration_of_lessons=Booking.LessonDuration.FORTY_FIVE_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.TWO_WEEKS,
            day_of_the_week=Booking.DayOfWeek.MONDAY,
            further_information="Extra Information"
        )

        self.booking2 = Booking.objects.create(
            user = User.objects.get(email="janedoe@email.com"),
            student_name="Jane Doe",
            invoice_id="0002-001",
            time_of_the_day="9:00",
            teacher="Mr Singh",
            number_of_lessons=15,
            start_date="2022-11-22",
            duration_of_lessons=Booking.LessonDuration.THIRTY_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.ONE_WEEK,
            day_of_the_week=Booking.DayOfWeek.TUESDAY,
            further_information="Extra Information 2"
        )


    def _assert_request_is_valid(self):
        try:
            self.booking1.full_clean()
        except (ValidationError):
            self.fail('Test request should be valid.')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booking1.full_clean()

    def test_booking_is_valid(self):
        self._assert_request_is_valid()

    def test_invoice_id_cannot_be_blank(self):
        self.booking1.invoice_id = ''
        self._assert_request_is_invalid()

    def test_start_date_can_be_in_the_past(self):
        self.booking1.date = timezone.datetime(2021, 12, 30, 1, 1, 1, tzinfo=timezone.utc)
        self._assert_request_is_valid()

    def test_start_date_can_be_today(self):
        self.booking1.date = timezone.datetime.now(tz=timezone.utc)
        self._assert_request_is_valid()

    def test_start_date_can_be_in_the_future(self):
        self.booking1.date = timezone.datetime(9999, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
        self._assert_request_is_valid()

    def test_user_must_exist(self):
        self.booking1.user.delete()
        self._assert_request_is_invalid()

    def test_user_may_be_the_same(self):
        self.booking1.user = self.booking2.user
        self._assert_request_is_valid()

    def test_time_and_day_may_be_the_same(self):
        self.booking1.day_of_the_week = self.booking2.day_of_the_week
        self.booking1.time_of_the_day = self.booking2.time_of_the_day
        self._assert_request_is_valid()

    def test_teacher_may_be_The_same(self):
        self.booking1.teacher = self.booking2.teacher
        self._assert_request_is_valid()

    def test_further_information_can_be_500_characters_long(self):
        self.booking1.further_information = 'x'*500
        self._assert_request_is_valid()

    def test_further_information_cannot_be_over_500_characters_long(self):
        self.booking1.further_information = 'x'*501
        self._assert_request_is_invalid()

    def test_duration_of_lessons_may_be_the_same(self):
        self.booking1.duration_of_lessons = self.booking2.duration_of_lessons
        self._assert_request_is_valid()

    def test_interval_between_lessons_may_be_the_same(self):
        self.booking1.interval_between_lessons = self.booking2.interval_between_lessons
        self._assert_request_is_valid()

    def test_number_of_lessons_may_be_the_same(self):
        self.booking1.number_of_lessons = self.booking2.number_of_lessons
        self._assert_request_is_valid()

    def test_further_information_may_be_the_same(self):
        self.booking1.further_information = self.booking2.further_information
        self._assert_request_is_valid()

    def test_invoice_id_cannot_be_the_same(self):
        self.booking1.invoice_id = self.booking2.invoice_id
        self._assert_request_is_invalid()

    def test_invoice_id_cannot_be_less_than_8_characters(self):
        self.booking1.invoice_id = "0001-01"
        self._assert_request_is_invalid()
    def test_invoice_id_cannot_be_more_than_8_characters(self):
        self.booking1.invoice_id = "0001-0001"
        self._assert_request_is_invalid()

    def test_number_of_lessons_cannot_be_below_one(self):
        self.booking1.number_of_lessons = 0
        self._assert_request_is_invalid()