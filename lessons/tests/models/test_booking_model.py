from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import User, DayOfTheWeek, Booking, SchoolTerm, Invoice, Student
from django.utils import timezone
from lessons.tests.helpers import create_user_groups, create_days_of_the_week
import datetime


class BookingModelTestCase(TestCase):
    '''Unit test for the Booking model'''
    
    fixtures = ['lessons/tests/fixtures/other_users.json', 'lessons/tests/fixtures/default_user.json']

    def setUp(self):
        create_user_groups()
        create_days_of_the_week()
        Student(user=User.objects.get(email="johndoe@email.com"), balance=0).save()
        Student(user=User.objects.get(email="janedoe@email.com"), balance=0).save()
        SchoolTerm(term_name="Term one", start_date=datetime.date(2022, 9, 1),
                   end_date=datetime.date(2022, 10, 21)).save()
        SchoolTerm(term_name="Term two", start_date=datetime.date(2022, 10, 31),
                   end_date=datetime.date(2022, 12, 16)).save()
        i1 = Invoice(invoice_number="0001-001", student=Student.objects.get(user__email="johndoe@email.com"),
                     full_amount=300, paid_amount=0, fully_paid=False)
        i2 = Invoice(invoice_number="0002-001", student=Student.objects.get(user__email="janedoe@email.com"),
                     full_amount=500, paid_amount=0, fully_paid=False)
        i1.save()
        i2.save()

        self.booking1 = Booking.objects.create(
            user=User.objects.get(email="johndoe@email.com"),
            relation_id=1,
            invoice=i1,
            time_of_the_day="12:00",
            teacher="Mr Smith",
            number_of_lessons=20,
            start_date="2022-11-21",
            end_date="2023-11-21",
            term_id=SchoolTerm.objects.get(term_name="Term one"),
            duration_of_lessons=Booking.LessonDuration.FORTY_FIVE_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.TWO_WEEKS,
            day_of_the_week=DayOfTheWeek.objects.get(order=1),
            further_information="Extra Information"
        )

        self.booking2 = Booking.objects.create(
            user=User.objects.get(email="janedoe@email.com"),
            relation_id=2,
            invoice=i2,
            time_of_the_day="9:00",
            teacher="Mr Singh",
            number_of_lessons=15,
            start_date="2022-11-22",
            end_date="2023-11-22",
            term_id=SchoolTerm.objects.get(term_name="Term two"),
            duration_of_lessons=Booking.LessonDuration.THIRTY_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.ONE_WEEK,
            day_of_the_week=DayOfTheWeek.objects.get(order=2),
            further_information="Extra Information 2"
        )

    def _assert_booking_is_valid(self):
        try:
            self.booking1.full_clean()
        except ValidationError:
            self.fail('Test booking should be valid.')

    def _assert_booking_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booking1.full_clean()

    def test_booking_is_valid(self):
        self._assert_booking_is_valid()

    def test_invoice_must_exist(self):
        self.booking1.invoice = None
        self._assert_booking_is_invalid()

    def test_start_date_can_be_in_the_past(self):
        self.booking1.date = timezone.datetime(2021, 12, 30, 1, 1, 1, tzinfo=timezone.utc)
        self._assert_booking_is_valid()

    def test_start_date_can_be_today(self):
        self.booking1.date = timezone.datetime.now(tz=timezone.utc)
        self._assert_booking_is_valid()

    def test_start_date_can_be_in_the_future(self):
        self.booking1.date = timezone.datetime(9999, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
        self._assert_booking_is_valid()

    def test_user_must_exist(self):
        self.booking1.user.delete()
        self._assert_booking_is_invalid()

    def test_user_may_be_the_same(self):
        self.booking1.user = self.booking2.user
        self._assert_booking_is_valid()
    
    def test_relation_id_may_be_the_same(self):
        self.booking1.relation_id = self.booking2.relation_id
        self._assert_booking_is_valid()
    
    def test_relation_id_cannot_be_below_negative_one(self):
        self.booking1.relation_id = -2
        self._assert_booking_is_invalid()
    
    def test_relation_id_can_be_negative_one(self):
        self.booking1.relation_id = -1
        self._assert_booking_is_valid()

    def test_time_and_day_may_be_the_same(self):
        self.booking1.day_of_the_week = self.booking2.day_of_the_week
        self.booking1.time_of_the_day = self.booking2.time_of_the_day
        self._assert_booking_is_valid()

    def test_teacher_may_be_The_same(self):
        self.booking1.teacher = self.booking2.teacher
        self._assert_booking_is_valid()

    def test_further_information_can_be_500_characters_long(self):
        self.booking1.further_information = 'x' * 500
        self._assert_booking_is_valid()

    def test_further_information_cannot_be_over_500_characters_long(self):
        self.booking1.further_information = 'x' * 501
        self._assert_booking_is_invalid()

    def test_duration_of_lessons_may_be_the_same(self):
        self.booking1.duration_of_lessons = self.booking2.duration_of_lessons
        self._assert_booking_is_valid()

    def test_interval_between_lessons_may_be_the_same(self):
        self.booking1.interval_between_lessons = self.booking2.interval_between_lessons
        self._assert_booking_is_valid()

    def test_number_of_lessons_may_be_the_same(self):
        self.booking1.number_of_lessons = self.booking2.number_of_lessons
        self._assert_booking_is_valid()

    def test_further_information_may_be_the_same(self):
        self.booking1.further_information = self.booking2.further_information
        self._assert_booking_is_valid()

    def test_invoice_id_cannot_be_the_same(self):
        self.booking1.invoice = self.booking2.invoice
        self._assert_booking_is_invalid()

    def test_number_of_lessons_cannot_be_below_one(self):
        self.booking1.number_of_lessons = 0
        self._assert_booking_is_invalid()
