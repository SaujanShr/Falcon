"""Unit tests of the booking edit form"""
import datetime

from django.test import TestCase
from lessons.models import User, Request, SchoolTerm, DayOfTheWeek, Student, Booking, Invoice
from lessons.forms import BookingEditForm
from django.utils import timezone
from django import forms
from lessons.tests.helpers import create_days_of_the_week, create_user_groups

class BookingEditFormTestCase(TestCase):
    """Unit tests for the Booking Edit form"""

    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/default_terms.json']

    def setUp(self):
        create_days_of_the_week()
        create_user_groups()

        # Create form inputs
        student = Student.objects.create(
            user=User.objects.all()[0],
            balance=100
        )

        self.request=Request.objects.create(
            user=User.objects.all()[0],
            number_of_lessons=1,
            relation_id=-1,
            interval_between_lessons=Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons=Request.LessonDuration.THIRTY_MINUTES,
            further_information='Some information',
        )

        i1 = Invoice(invoice_number="0001-001", student=Student.objects.get(user__email="johndoe@email.com"),
                     full_amount=300, paid_amount=0, fully_paid=False)
        i1.save()

        self.booking1 = Booking.objects.create(
            user=User.objects.get(email="johndoe@email.com"),
            relation_id=1,
            invoice=i1,
            time_of_the_day="12:00",
            teacher="Mr Smith",
            number_of_lessons=20,
            start_date="2022-01-01",
            end_date="2022-11-21",
            term_id=SchoolTerm.objects.all()[0],
            duration_of_lessons=Booking.LessonDuration.FORTY_FIVE_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.TWO_WEEKS,
            day_of_the_week=DayOfTheWeek.objects.get(order=0),
            further_information="Extra Information"
        )

        self.term = SchoolTerm.objects.all()[0]

        self.form_input = {
            'time_of_the_day': self.booking1.time_of_the_day,
            'day_of_the_week': self.booking1.day_of_the_week,
            'user': self.booking1.user,
            'relation_id': self.booking1.relation_id,
            'teacher': self.booking1.teacher,
            'start_date': self.booking1.start_date,
            'end_date': self.booking1.end_date,
            'duration_of_lessons': self.booking1.duration_of_lessons,
            'interval_between_lessons': self.booking1.interval_between_lessons,
            'number_of_lessons': self.booking1.number_of_lessons,
            'further_information': self.booking1.further_information,
            'hourly_cost': 20
        }

    def _assert_form_is_valid(self):
        form = BookingEditForm(instance_id=self.booking1.id, data=self.form_input)
        self.assertTrue(form.is_valid())

    def _assert_form_is_invalid(self):
        form = BookingEditForm(instance_id=self.booking1.id, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_valid_fulfil_request_form(self):
        self._assert_form_is_valid()

    def test_form_has_necessary_fields(self):
        form = BookingEditForm(instance_id=self.booking1.id, data=self.form_input)

        self.assertIn('day_of_the_week', form.fields)
        self.assertIn('time_of_the_day', form.fields)
        self.assertIn('teacher', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('interval_between_lessons', form.fields)
        self.assertIn('end_date', form.fields)
        self.assertIn('hourly_cost', form.fields)
        self.assertIn('duration_of_lessons', form.fields)
        self.assertIn('number_of_lessons', form.fields)
        self.assertIn('further_information', form.fields)

    def test_form_fields_have_correct_initial_values(self):
        form = BookingEditForm(instance_id=self.booking1.id, data=self.form_input)

        self.assertEqual(form['start_date'].value(), self.booking1.start_date)
        self.assertEqual(form['end_date'].value(), self.booking1.end_date)
        self.assertEqual(form['number_of_lessons'].value(), self.booking1.number_of_lessons)
        self.assertEqual(form['interval_between_lessons'].value(), self.booking1.interval_between_lessons)
        self.assertEqual(form['duration_of_lessons'].value(), self.booking1.duration_of_lessons)
        self.assertEqual(form['further_information'].value(), self.booking1.further_information)
        self.assertEqual(form['day_of_the_week'].value(), 1) #Monday
        self.assertEqual(form['hourly_cost'].value(), 20)

    def test_day_of_the_week_must_exist(self):
        self.form_input['day_of_the_week'] = None
        self._assert_form_is_invalid()

    def test_time_of_lesson_cannot_be_blank(self):
        self.form_input['time_of_the_day'] = ''
        self._assert_form_is_invalid()

    def test_time_of_lesson_can_be_current_time(self):
        self.form_input['time_of_lesson'] = timezone.now().time()
        self._assert_form_is_valid()

    def test_start_date_cannot_be_blank(self):
        self.form_input['start_date'] = ''
        self._assert_form_is_invalid()

    def test_start_date_cannot_be_before_current_date(self):
        self.form_input['start_date'] = '0000-00-00'
        self._assert_form_is_invalid()

    def test_end_date_cannot_be_blank(self):
        self.form_input['end_date'] = ''
        self._assert_form_is_invalid()

    def test_end_date_cannot_be_before_current_date(self):
        self.form_input['end_date'] = '0000-00-00'
        self._assert_form_is_invalid()

    def test_start_date_cannot_be_after_end_date(self):
        self.form_input['end_date'] = '9999-00-00'
        self._assert_form_is_invalid()

    def test_teacher_cannot_be_blank(self):
        self.form_input['teacher'] = ''
        self._assert_form_is_invalid()

    def test_teacher_may_contain_100_characters(self):
        self.form_input['teacher'] = 'x' * 100

    def test_number_of_lessons_cannot_be_below_one(self):
        self.form_input['number_of_lessons'] = 0
        self._assert_form_is_invalid()

    def test_number_of_lessons_can_be_one(self):
        self.form_input['number_of_lessons'] = 1
        self._assert_form_is_valid()

    def test_number_of_lessons_cannot_be_over_1000(self):
        self.form_input['number_of_lessons'] = 1001
        self._assert_form_is_invalid()

    def test_number_of_lessons_may_be_1000(self):
        self.form_input['number_of_lessons'] = 1000
        self._assert_form_is_valid()

    def test_interval_between_lessons_cannot_be_blank(self):
        self.form_input['interval_between_lessons'] = ''
        self._assert_form_is_invalid()

    def test_duration_of_lessons_cannot_be_blank(self):
        self.form_input['duration_of_lessons'] = ''
        self._assert_form_is_invalid()

    def test_further_information_cannot_be_blank(self):
        self.form_input['further_information'] = ''
        self._assert_form_is_invalid()

    def test_further_information_cannot_contain_over_500_characters(self):
        self.form_input['further_information'] = 'x' * 501
        self._assert_form_is_invalid()

    def test_further_information_may_contain_500_characters(self):
        self.form_input['further_information'] = 'x' * 500
        self._assert_form_is_valid()

    def test_values_can_be_updated(self):
        form_input2 = {
            'time_of_the_day': '14:00',
            'day_of_the_week': self.booking1.day_of_the_week,
            'user': self.booking1.user,
            'relation_id': self.booking1.relation_id,
            'teacher': self.booking1.teacher,
            'start_date': self.booking1.start_date,
            'end_date': self.booking1.end_date,
            'duration_of_lessons': self.booking1.duration_of_lessons,
            'interval_between_lessons': self.booking1.interval_between_lessons,
            'number_of_lessons': self.booking1.number_of_lessons,
            'further_information': "Updated information.",
            'hourly_cost': 20
        }
        form = BookingEditForm(instance_id=self.booking1.id, data=form_input2)
        form.save()
        self.assertEqual(Booking.objects.get(id=self.booking1.id).time_of_the_day, datetime.time(14))
        self.assertEqual(Booking.objects.get(id=self.booking1.id).further_information, 'Updated information.')

    def test_invoice_gets_updated_when_hourly_cost_changed(self):
        form_input2 = {
            'time_of_the_day': self.booking1.time_of_the_day,
            'day_of_the_week': self.booking1.day_of_the_week,
            'user': self.booking1.user,
            'relation_id': self.booking1.relation_id,
            'teacher': self.booking1.teacher,
            'start_date': self.booking1.start_date,
            'end_date': self.booking1.end_date,
            'duration_of_lessons': self.booking1.duration_of_lessons,
            'interval_between_lessons': self.booking1.interval_between_lessons,
            'number_of_lessons': self.booking1.number_of_lessons,
            'further_information': self.booking1.further_information,
            'hourly_cost': 30
        }
        form = BookingEditForm(instance_id=self.booking1.id, data=form_input2)
        form.save()

        self.assertEqual(Booking.objects.get(id=self.booking1.id).invoice.full_amount, 450)

    def test_invoice_gets_updated_when_duration_of_lesson_changed(self):
        form_input2 = {
            'time_of_the_day': self.booking1.time_of_the_day,
            'day_of_the_week': self.booking1.day_of_the_week,
            'user': self.booking1.user,
            'relation_id': self.booking1.relation_id,
            'teacher': self.booking1.teacher,
            'start_date': self.booking1.start_date,
            'end_date': self.booking1.end_date,
            'duration_of_lessons': Booking.LessonDuration.THIRTY_MINUTES,
            'interval_between_lessons': self.booking1.interval_between_lessons,
            'number_of_lessons': self.booking1.number_of_lessons,
            'further_information': self.booking1.further_information,
            'hourly_cost': 20
        }
        form = BookingEditForm(instance_id=self.booking1.id, data=form_input2)
        form.save()

        self.assertEqual(Booking.objects.get(id=self.booking1.id).invoice.full_amount, 200)

    def test_term_is_calculated_correctly_even_when_lessons_start_outside_of_term(self):
        form_input = {
            'time_of_the_day': self.booking1.time_of_the_day,
            'day_of_the_week': self.booking1.day_of_the_week,
            'user': self.booking1.user,
            'relation_id': self.booking1.relation_id,
            'teacher': self.booking1.teacher,
            'start_date': (self.term.end_date + datetime.timedelta(days=1)),
            'end_date': self.booking1.end_date,
            'duration_of_lessons': self.booking1.duration_of_lessons,
            'interval_between_lessons': self.booking1.interval_between_lessons,
            'number_of_lessons': self.booking1.number_of_lessons,
            'further_information': self.booking1.further_information,
            'hourly_cost': 20
        }
        form = BookingEditForm(instance_id=self.booking1.id, data=form_input)
        form.save()

        self.assertEqual(Booking.objects.get(id=self.booking1.id).term_id, SchoolTerm.objects.all()[0])









