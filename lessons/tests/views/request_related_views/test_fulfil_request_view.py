"""Tests of the fulfil request view."""
import datetime

from django.test import TestCase
from django.urls import reverse
from lessons.forms import FulfilRequestForm
from lessons.models import Request, DayOfTheWeek, SchoolTerm, Booking, User, Student
from lessons.tests.helpers import create_user_groups, HandleGroups, create_days_of_the_week


class NewRequestViewTestCase(TestCase):
    """Tests of the fulfil request view"""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/default_terms.json',
                'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        HandleGroups.set_default_user_to_admin()
        self.client.login(email="johndoe@email.com", password="Password123")



        create_days_of_the_week()

        self.term = SchoolTerm.objects.all()[0]
        student = Student.objects.create(user=User.objects.all()[0])
        student.save()
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

        self.form_input = {
            'time_of_lesson': '10:20',
            'availability': DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.MONDAY),
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

        self.url = reverse('fulfil_request') + "?request_id=" + str(self.request.id)

    def test_new_request_url(self):
        self.assertEqual(self.url, '/fulfil_request/?request_id='+str(self.request.id))

    def test_student_cannot_access_school_terms_admin_edit_view(self):
        self.client.login(email='janedoe@email.com', password='Password123')
        HandleGroups.set_other_user_to_student()
        response = self.client.get(self.url, follow=True)

        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_fulfil_request_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fulfil_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, FulfilRequestForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_fulfilment(self):
        self.form_input['number_of_lessons'] = -1
        before_count = Booking.objects.count()
        payload = {'request_id': 1, 'fulfil': ' ',
                   'time_of_lesson': datetime.time(14),
                   'availability': 1,
                   'user': self.request.user,
                   'teacher': 'Joe Swinden',
                   'start_date': self.term.start_date,
                   'end_date': self.term.end_date,
                   'duration_of_lessons': self.request.duration_of_lessons,
                   'interval_between_lessons': self.request.interval_between_lessons,
                   'number_of_lessons': -1, #Invalid
                   'further_information': self.request.further_information,
                   'hourly_cost': 15
                   }
        response = self.client.post(self.url, payload, follow=True)
        after_count = Booking.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_booking_list.html')

    def test_successful_new_request(self):
        before_count = Booking.objects.count()
        payload = {'request_id': 1, 'fulfil': ' ',
                   'time_of_lesson': datetime.time(14),
                   'availability': 1,
                   'user': self.request.user,
                   'teacher': 'Joe Swinden',
                   'start_date': self.term.start_date,
                   'end_date': self.term.end_date,
                   'duration_of_lessons': self.request.duration_of_lessons,
                   'interval_between_lessons': self.request.interval_between_lessons,
                   'number_of_lessons': 1,
                   'further_information': self.request.further_information,
                   'hourly_cost': 15
                   }
        response = self.client.post(self.url, payload, follow=True)
        after_count = Booking.objects.count()
        response_url = reverse('admin_booking_list')
        self.assertRedirects(response, response_url, status_code=302,
                             target_status_code=200)
        self.assertEqual(after_count, before_count + 1)  # Check that the Booking count has increased by 1

        self.assertTemplateUsed(response, 'admin_booking_list.html')

        booking = Booking.objects.all()[:1].get()
        self.assertEqual(booking.number_of_lessons, self.request.number_of_lessons)
        self.assertEqual(booking.interval_between_lessons, self.request.interval_between_lessons)
        self.assertEqual(booking.duration_of_lessons, self.request.duration_of_lessons)
        self.assertEqual(booking.further_information, self.request.further_information)

    def test_return_function_works_even_with_invalid_data_in_form(self):

        payload = {'request_id': 1, 'return': ' ',
                   'time_of_lesson': datetime.time(14),
                   'availability': 1,
                   'user': self.request.user,
                   'teacher': 'Joe Swinden',
                   'start_date': self.term.start_date,
                   'end_date': self.term.end_date,
                   'duration_of_lessons': self.request.duration_of_lessons,
                   'interval_between_lessons': self.request.interval_between_lessons,
                   'number_of_lessons': -1, #Invalid
                   'further_information': self.request.further_information,
                   'hourly_cost': 15
                   }
        response = self.client.post(self.url, payload, follow=True)
        response_url = reverse('admin_request_list')
        self.assertRedirects(response, response_url, status_code=302,
                             target_status_code=200)

    def test_delete_function_works_even_with_invalid_data_in_form(self):
        before_count = Request.objects.count()
        payload = {'request_id': 1, 'delete': ' ',
                   'time_of_lesson': datetime.time(14),
                   'availability': 1,
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
        response = self.client.post(self.url, payload, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count + 1, before_count)
        response_url = reverse('admin_request_list')
        self.assertRedirects(response, response_url, status_code=302,
                             target_status_code=200)


