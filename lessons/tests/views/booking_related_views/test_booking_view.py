"""Tests of the booking view."""
import datetime

from django.test import TestCase
from django.urls import reverse
from lessons.forms import BookingEditForm
from lessons.models import Request, DayOfTheWeek, Booking, User, Student, Invoice, SchoolTerm
from lessons.tests.helpers import create_user_groups, HandleGroups, create_days_of_the_week
from django.utils import timezone


class RequestViewTestCase(TestCase):
    """Tests of the request view"""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json',
                'lessons/tests/fixtures/default_terms.json']

    def setUp(self):
        create_user_groups()
        HandleGroups.set_default_user_to_admin()
        HandleGroups.set_other_user_to_student()
        self.client.login(email="johndoe@email.com", password="Password123")

        self.url = reverse('booking_view')

        create_days_of_the_week()

        self.request = Request.objects.create(
            user=User.objects.all()[0],
            number_of_lessons=1,
            relation_id=-1,
            interval_between_lessons=Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons=Request.LessonDuration.THIRTY_MINUTES,
            further_information='Some information',
            fulfilled=False
        )
        self.request.availability.set([DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.MONDAY),
                                        DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.WEDNESDAY),
                                        DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.SUNDAY)])

        self.request.save()

        self.term = SchoolTerm.objects.all()[0]

        self.form_input = {
            'time_of_lesson': '10:20',
            'availability': 1,
            'user': self.request.user,
            'relation_id': self.request.relation_id,
            'teacher': 'Joe Swinden',
            'start_date': self.term.start_date,
            'end_date': self.term.end_date,
            'duration_of_lessons': self.request.duration_of_lessons,
            'interval_between_lessons': self.request.interval_between_lessons,
            'number_of_lessons': self.request.number_of_lessons,
            'further_information': self.request.further_information,
            'hourly_cost': 15
        }

        student = Student.objects.create(user=User.objects.all()[0])
        student.save()

        student2 = Student.objects.create(user=User.objects.all()[1])
        student2.save()

        i1 = Invoice(
            invoice_number="0001-001",
            student=Student.objects.get(user__email="johndoe@email.com"),
            full_amount=300,
            paid_amount=299,
            fully_paid=False
        )
        i1.save()

        i2 = Invoice(
            invoice_number="0002-001",
            student=Student.objects.get(user__email="janedoe@email.com"),
            full_amount=500,
            paid_amount=499,
            fully_paid=False
        )
        i2.save()



        self.booking1 = Booking.objects.create(
            user=User.objects.get(email="johndoe@email.com"),
            relation_id=-1,
            invoice=i1,
            time_of_the_day="12:00",
            teacher="Mr Smith",
            number_of_lessons=20,
            start_date="2022-11-21",
            end_date="2023-11-21",
            term_id=SchoolTerm.objects.all()[0],
            duration_of_lessons=Booking.LessonDuration.FORTY_FIVE_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.TWO_WEEKS,
            day_of_the_week=DayOfTheWeek.objects.get(order=1),
            further_information="Extra Information"
        )

        self.booking1.save()

        self.booking2 = Booking.objects.create(
            user=User.objects.get(email="janedoe@email.com"),
            relation_id=-1,
            invoice=i2,
            time_of_the_day="12:00",
            teacher="Mr Smith",
            number_of_lessons=20,
            start_date="2022-11-21",
            end_date="2023-11-21",
            term_id=SchoolTerm.objects.all()[0],
            duration_of_lessons=Booking.LessonDuration.FORTY_FIVE_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.TWO_WEEKS,
            day_of_the_week=DayOfTheWeek.objects.get(order=1),
            further_information="Extra Information"
        )

        self.booking2.save()

    def test_request_url(self):
        self.assertEqual(self.url, '/booking_view/')

    def test_get_request_view(self):
        response = self.client.get(self.url + "?booking_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, BookingEditForm))
        self.assertFalse(form.is_bound)

    def test_get_request_of_another_student_redirects(self):
        self.client.login(email="janedoe@email.com", password="Password123")
        response = self.client.get(self.url + "?booking_id=1", follow=True)
        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_read_only_for_user(self):
        self.client.login(email="janedoe@email.com", password="Password123")
        payload = {'booking_id': 2, 'relation_id': -1}
        response = self.client.get(self.url + "?booking_id=1", payload, follow=True)
        self.assertTemplateUsed(response, 'booking_view.html')

        form = response.context['form']
        self.assertTrue(form.fields['day_of_the_week'].disabled)
        self.assertTrue(form.fields['time_of_the_day'].disabled)
        self.assertTrue(form.fields['teacher'].disabled)
        self.assertTrue(form.fields['start_date'].disabled)
        self.assertTrue(form.fields['end_date'].disabled)
        self.assertTrue(form.fields['hourly_cost'].disabled)
        self.assertTrue(form.fields['number_of_lessons'].disabled)
        self.assertTrue(form.fields['interval_between_lessons'].disabled)
        self.assertTrue(form.fields['duration_of_lessons'].disabled)
        self.assertTrue(form.fields['further_information'].disabled)

    def test_booking_redirect_on_return_button(self):
        payload = {'booking_id': 1, 'return': ' ',
                   'time_of_the_day': datetime.time(14),
                   'day_of_the_week': 1,
                   'availability': 1,
                   'relation_id': -1,
                   'user': self.request.user,
                   'teacher': 'Joe Swinden',
                   'start_date': self.term.start_date,
                   'end_date': self.term.end_date,
                   'duration_of_lessons': self.request.duration_of_lessons,
                   'interval_between_lessons': self.request.interval_between_lessons,
                   'number_of_lessons': -1,  # Invalid
                   'further_information': self.request.further_information,
                   'hourly_cost': 15
                   }
        response = self.client.post(self.url + "?booking_id=1", payload, follow=True)
        response_url = reverse('admin_booking_list')+"?relation_id=-1"
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_booking_list.html')

    def test_booking_deletion_with_delete_button(self):
        payload = {'booking_id': 1, 'delete': ' ',
                   'time_of_the_day': datetime.time(14),
                   'day_of_the_week': 1,
                   'availability': 1,
                   'relation_id': -1,
                   'user': self.request.user,
                   'teacher': 'Joe Swinden',
                   'start_date': self.term.start_date,
                   'end_date': self.term.end_date,
                   'duration_of_lessons': self.request.duration_of_lessons,
                   'interval_between_lessons': self.request.interval_between_lessons,
                   'number_of_lessons': -1,  # Invalid
                   'further_information': self.request.further_information,
                   'hourly_cost': 15
                   }
        before_count = Booking.objects.count()
        response = self.client.post(self.url + "?booking_id=1", payload, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(before_count, after_count + 1)
        response_url = reverse('admin_booking_list')+"?relation_id=-1"
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_booking_list.html')

    def test_successful_booking_edit(self):
        payload = {'booking_id': 1, 'update': ' ',
                   'time_of_the_day': datetime.time(14),
                   'day_of_the_week': 1,
                   'availability': 1,
                   'relation_id': -1,
                   'user': self.request.user,
                   'teacher': 'Joe Swinden',
                   'start_date': self.term.start_date,
                   'end_date': self.term.end_date,
                   'duration_of_lessons': self.request.duration_of_lessons,
                   'interval_between_lessons': self.request.interval_between_lessons,
                   'number_of_lessons': 32,
                   'further_information': self.request.further_information,
                   'hourly_cost': 15
                   }
        before_count = Booking.objects.count()
        response = self.client.post(self.url + "?booking_id=1", payload, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('admin_booking_list')+"?relation_id=-1"
        self.assertEqual(Booking.objects.get(id=1).number_of_lessons, 32)
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_booking_list.html')

    def test_unsuccessful_booking_edit(self):
        payload = {'booking_id': 1, 'update': ' ',
                   'time_of_the_day': datetime.time(14),
                   'day_of_the_week': 1,
                   'availability': 1,
                   'relation_id': -1,
                   'user': self.request.user,
                   'teacher': 'Joe Swinden',
                   'start_date': self.term.start_date,
                   'end_date': self.term.end_date,
                   'duration_of_lessons': self.request.duration_of_lessons,
                   'interval_between_lessons': self.request.interval_between_lessons,
                   'number_of_lessons': -1,
                   'further_information': self.request.further_information,
                   'hourly_cost': 15
                   }
        before_count = Booking.objects.count()
        response = self.client.post(self.url + "?request_id=1", payload, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(Booking.objects.get(id=1).number_of_lessons, 20)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_view.html')
