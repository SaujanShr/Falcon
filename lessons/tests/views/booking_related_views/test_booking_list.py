"""Unit tests of the booking list view."""
from django.test import TestCase
from lessons.models import User, DayOfTheWeek, Booking, SchoolTerm, Invoice, Student
from lessons.tests.helpers import create_user_groups, create_days_of_the_week
from django.urls import reverse
import datetime


class LessonGenerationTestCase(TestCase):
    """Unit tests of the booking list view."""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        create_days_of_the_week()
        Student(user=User.objects.get(email="johndoe@email.com"), balance=0).save()
        Student(user=User.objects.get(email="janedoe@email.com"), balance=0).save()
        SchoolTerm(term_name="Term one", start_date=datetime.date(2029, 9, 1),
                   end_date=datetime.date(2029, 10, 21)).save()
        SchoolTerm(term_name="Term two", start_date=datetime.date(2029, 10, 31),
                   end_date=datetime.date(2029, 12, 16)).save()
        Invoice(invoice_number="0001-001", student=Student.objects.get(user__email="johndoe@email.com"),
                full_amount=300, paid_amount=0, fully_paid=False).save()
        Invoice(invoice_number="0002-001", student=Student.objects.get(user__email="janedoe@email.com"),
                full_amount=500, paid_amount=0, fully_paid=False).save()

        self.booking1 = Booking.objects.create(
            user=User.objects.get(email="johndoe@email.com"),
            relation_id=-1,
            invoice=Invoice.objects.get(invoice_number="0001-001"),
            time_of_the_day="12:00",
            teacher="Mr Smith",
            number_of_lessons=4,
            start_date="2029-11-21",
            end_date="2029-11-21",
            term_id=SchoolTerm.objects.get(term_name="Term one"),
            duration_of_lessons=Booking.LessonDuration.FORTY_FIVE_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.TWO_WEEKS,
            day_of_the_week=DayOfTheWeek.objects.get(order=1),
            further_information="Extra Information"
        )

        self.booking2 = Booking.objects.create(
            user=User.objects.get(email="janedoe@email.com"),
            relation_id=-1,
            invoice=Invoice.objects.get(invoice_number="0002-001"),
            time_of_the_day="9:00",
            teacher="Mr Singh",
            number_of_lessons=5,
            start_date="2029-11-22",
            end_date="2029-11-22",
            term_id=SchoolTerm.objects.get(term_name="Term two"),
            duration_of_lessons=Booking.LessonDuration.THIRTY_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.ONE_WEEK,
            day_of_the_week=DayOfTheWeek.objects.get(order=2),
            further_information="Extra Information 2"
        )

        self.url = reverse('booking_list')
        self.client.login(email='johndoe@email.com', password='Password123')

    def test_lesson_list_url(self):
        self.assertEqual(self.url, '/booking_list/')

    def test_get_booking_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_list.html')
        bookings = response.context['bookings']
        self.assertTrue(bookings)
        self.assertTrue(isinstance(bookings, list))

    def test_booking_list_displays_only_users_booking(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_list.html')
        bookings = response.context['bookings']
        user = User.objects.get(email="johndoe@email.com")
        self.assertEqual(len(bookings), len(Booking.objects.filter(user=user)))
