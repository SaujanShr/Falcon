"""Unit tests of the request edit view"""
from django.utils import timezone
from django.test import TestCase
from lessons.forms import RequestEditForm
from lessons.models import DayOfTheWeek, Request, User
from django import forms
from lessons.tests.helpers import create_days_of_the_week, HandleGroups


class RequestViewFormTestCase(TestCase):
    """Unit tests for the RequestViewForm form"""

    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        create_days_of_the_week()
        HandleGroups.set_default_user_to_student()

        # Create form inputs
        self.user = User.objects.all()[0]
        self.currentDate = timezone.datetime.now(tz=timezone.utc)
        availability = [DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY), 
                        DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.WEDNESDAY)]
        number_of_lessons = 1
        interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK
        duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES
        further_information = 'Some information'

        self.form_input = {
            'date': self.currentDate,
            'availability': availability,
            'number_of_lessons': number_of_lessons,
            'interval_between_lessons': interval_between_lessons,
            'duration_of_lessons': duration_of_lessons,
            'further_information': further_information,
            'fulfilled': ''
        }
        
    def _assert_form_is_valid(self):
        form = RequestEditForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        
    def _assert_form_is_invalid(self):
        form = RequestEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RequestEditForm()
        self.assertIn('date', form.fields)
        date_field = form.fields['date']
        self.assertTrue(isinstance(date_field, forms.DateTimeField))
        self.assertIn('availability', form.fields)
        self.assertIn('number_of_lessons', form.fields)
        self.assertIn('interval_between_lessons', form.fields)
        self.assertIn('duration_of_lessons', form.fields)
        self.assertIn('further_information', form.fields)
        self.assertIn('fulfilled', form.fields)

    def test_availability_cannot_accept_no_choices(self):
        self.form_input['availability'] = None
        self._assert_form_is_invalid()


    
    def test_availability_can_accept_multiple_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.THURSDAY)
        self._assert_form_is_valid()


    
    def test_availability_can_accept_all_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.MONDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.THURSDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.FRIDAY)
        self._assert_form_is_valid()

    def test_number_of_lessons_cannot_be_empty(self):
        self.form_input['number_of_lessons'] = None
        self._assert_form_is_invalid()

    def test_number_of_lessons_can_be_1(self):
        self.form_input['number_of_lessons'] = 1
        self._assert_form_is_valid()

    def test_number_of_lessons_can_greater_than_1(self):
        self.form_input['number_of_lessons'] = 2
        self._assert_form_is_valid()

    def test_number_of_lessons_cannot_be_less_than_1(self):
        self.form_input['number_of_lessons'] = 0
        self._assert_form_is_invalid()

    def test_number_of_lessons_can_be_1000(self):
        self.form_input['number_of_lessons'] = 1000
        self._assert_form_is_valid()

    def test_number_of_lessons_cannot_be_greater_than_1000(self):
        self.form_input['number_of_lessons'] = 1001
        self._assert_form_is_invalid()

    def test_interval_between_lessons_cannot_be_empty(self):
        self.form_input['interval_between_lessons'] = None
        self._assert_form_is_invalid()

    def test_duration_of_lessons_can_accept_30_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.THIRTY_MINUTES
        self._assert_form_is_valid()

    def test_duration_of_lessons_can_accept_45_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.FOURTY_FIVE_MINUTES
        self._assert_form_is_valid()

    def test_duration_of_lessons_can_accept_60_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.SIXTY_MINUTES
        self._assert_form_is_valid()

    def test_duration_of_lessons_cannot_be_empty(self):
        self.form_input['duration_of_lessons'] = None
        self._assert_form_is_invalid()

    def test_further_information_cannot_be_empty(self):
        self.form_input['further_information'] = ''
        self._assert_form_is_invalid()

    def test_further_information_can_be_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 500
        self._assert_form_is_valid()

    def test_further_information_cannot_be_over_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 501
        self._assert_form_is_invalid()

    def test_form_set_read_only(self):
        form = RequestEditForm(data=self.form_input)
        form.set_read_only()
        self.assertTrue(form.fields['availability'].disabled)
        self.assertTrue(form.fields['number_of_lessons'].disabled)
        self.assertTrue(form.fields['interval_between_lessons'].disabled)
        self.assertTrue(form.fields['duration_of_lessons'].disabled)
        self.assertTrue(form.fields['further_information'].disabled)

    # Todo: add form_must_save_properly()

    #This test is broken, the availability part.

    def test_form_must_save_properly(self):
        request = Request.objects.create(
            user=self.user,
            relation_id=-1,
            date=self.form_input['date'],
            number_of_lessons=self.form_input['number_of_lessons'],
            interval_between_lessons=self.form_input['interval_between_lessons'],
            duration_of_lessons=self.form_input['duration_of_lessons'],
            further_information=self.form_input['further_information']
        )
        request.availability.set(self.form_input['availability'])
        
        self.form_input['number_of_lessons'] = 10
        self.form_input['interval_between_lessons'] = Request.IntervalBetweenLessons.TWO_WEEKS
        self.form_input['availability'] = [DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.WEDNESDAY)]
        
        form = RequestEditForm(instance_id=request.id, data=self.form_input)
        before_count = Request.objects.count()
        request = form.save()
        after_count = Request.objects.count()
        
        self.assertEqual(before_count, after_count)
        
        self.assertEqual(request.date, self.form_input['date'])
        self.assertEqual(request.number_of_lessons, self.form_input['number_of_lessons'])
        self.assertEqual(request.interval_between_lessons, self.form_input['interval_between_lessons'])
        self.assertEqual(request.duration_of_lessons, self.form_input['duration_of_lessons'])
        self.assertEqual(request.further_information, self.form_input['further_information'])
        self.assertEqual(list(request.availability.all()), self.form_input['availability'])