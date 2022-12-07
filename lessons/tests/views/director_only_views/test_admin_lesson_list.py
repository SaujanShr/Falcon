"""Unit tests of the Admin lesson list."""
from django.test import TestCase
from lessons.models import User, DayOfTheWeek, Booking, SchoolTerm, Invoice, Student
from lessons.tests.helpers import create_user_groups, create_days_of_the_week
from django.urls import reverse
import datetime


class AdminLessonListTestCase(TestCase):
    """Unit tests of the Admin lesson list."""
    fixtures = ['lessons/tests/fixtures/default_user.json','lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        create_days_of_the_week()
        Student(user=User.objects.get(email="johndoe@email.com"), balance=0).save()
        Student(user=User.objects.get(email="janedoe@email.com"), balance=0).save()
        self.superuser = User.objects.create_superuser(
            email='admin@email.com',
            password='password'
        )

        SchoolTerm(term_name="Term one", start_date=datetime.date(2029, 9, 1),
                   end_date=datetime.date(2029, 10, 21)).save()
        SchoolTerm(term_name="Term two", start_date=datetime.date(2029, 10, 31),
                   end_date=datetime.date(2029, 12, 16)).save()
        i1 = Invoice(invoice_number="0001-001", student=Student.objects.get(user__email="johndoe@email.com"),
                     full_amount=300, paid_amount=0, fully_paid=False).save()
        i2 = Invoice(invoice_number="0002-001", student=Student.objects.get(user__email="janedoe@email.com"),
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

        self.url = reverse('lesson_list_admin')
        self.client.login(email='admin@email.com', password='password')

    def test_admin_lesson_list_url(self):
        self.assertEqual(self.url, '/lessons/admin')

    def test_get_admin_lesson_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_list.html')
        lessons = response.context['lessons']
        self.assertTrue(lessons)
        self.assertTrue(isinstance(lessons, list))

    def test_admin_lesson_list_displays_all_users_lessons(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lesson_list.html')
        lessons = response.context['lessons']
        expected_lessons = self.booking1.number_of_lessons + self.booking2.number_of_lessons
        self.assertEqual(len(lessons), expected_lessons)
