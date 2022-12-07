from django.test import TestCase
from lessons.models import User, Request, SchoolTerm, DayOfTheWeek
from lessons.forms import FulfilRequestForm
from lessons.tests.helpers import create_days_of_the_week
from django.utils import timezone


class FulfilRequestFormTestCase(TestCase):
    """Unit tests for the FulfilRequestForm form"""

    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/default_terms.json']

    def setUp(self):
        create_days_of_the_week()

        self.request = Request.objects.create(
            user=User.objects.all()[0],
            number_of_lessons=1,
            relation_id=-1,
            interval_between_lessons=Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons=Request.LessonDuration.THIRTY_MINUTES,
            further_information='Some information',
        )
        self.term = SchoolTerm.objects.all()[0]

        self.request.availability.set([
            DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY),
            DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.WEDNESDAY)
        ])

        self.form_input = {
            'time_of_lesson': '10:10',
            'availability': DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY),
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

    def _assert_form_is_valid(self):
        form = FulfilRequestForm(request_id=self.request.id, data=self.form_input)
        self.assertTrue(form.is_valid())

    def _assert_form_is_invalid(self):
        form = FulfilRequestForm(request_id=self.request.id, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_valid_fulfil_request_form(self):
        self._assert_form_is_valid()

    def test_form_has_necessary_fields(self):
        form = FulfilRequestForm()

        self.assertIn('availability', form.fields)
        self.assertIn('time_of_lesson', form.fields)
        self.assertIn('teacher', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)
        self.assertIn('hourly_cost', form.fields)
        self.assertIn('duration_of_lessons', form.fields)
        self.assertIn('number_of_lessons', form.fields)
        self.assertIn('further_information', form.fields)

    def test_form_fields_have_correct_initial_values(self):
        form = FulfilRequestForm(request_id=self.request.id, data=self.form_input)

        self.assertEqual(form['start_date'].value(), self.term.start_date)
        self.assertEqual(form['end_date'].value(), self.term.end_date)
        self.assertEqual(form['number_of_lessons'].value(), self.request.number_of_lessons)
        self.assertEqual(form['interval_between_lessons'].value(), self.request.interval_between_lessons)
        self.assertEqual(form['duration_of_lessons'].value(), self.request.duration_of_lessons)
        self.assertEqual(form['further_information'].value(), self.request.further_information)

    def test_availability_must_exist(self):
        self.form_input['availability'] = None
        self._assert_form_is_invalid()

    def test_time_of_lesson_cannot_be_blank(self):
        self.form_input['time_of_lesson'] = ''
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
