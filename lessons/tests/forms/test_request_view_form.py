"""Unit tests of the request edit view"""
from django.utils import timezone
from django.test import TestCase
from lessons.forms import RequestViewForm
from lessons.models import DayOfTheWeek, Request
from django import forms
from lessons.tests.helpers import create_days_of_the_week, HandleGroups


class RequestViewFormTestCase(TestCase):
    """Unit tests of the request edit view"""

    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        create_days_of_the_week()
        HandleGroups.set_default_user_to_student()

        # Create form inputs
        self.currentDate = timezone.datetime.now(tz=timezone.utc)
        availability = DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY)
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

    def test_form_has_necessary_fields(self):
        form = RequestViewForm()
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
        form = RequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    
    def test_availability_can_accept_multiple_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.THURSDAY)
        form = RequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    
    def test_availability_can_accept_all_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.MONDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.THURSDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.FRIDAY)
        form = RequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_number_of_lessons_cannot_be_empty(self):
        self.form_input['number_of_lessons'] = None
        form = RequestViewForm(data=self.form_input)

        self.assertFalse(form.is_valid())

    def test_number_of_lessons_can_be_1(self):
        self.form_input['number_of_lessons'] = 1
        form = RequestViewForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_number_of_lessons_can_greater_than_1(self):
        self.form_input['number_of_lessons'] = 2
        form = RequestViewForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_number_of_lessons_cannot_be_less_than_1(self):
        self.form_input['number_of_lessons'] = 0
        form = RequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_number_of_lessons_can_be_1000(self):
        self.form_input['number_of_lessons'] = 1000
        form = RequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_number_of_lessons_cannot_be_greater_than_1000(self):
        self.form_input['number_of_lessons'] = 1001
        form = RequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_interval_between_lessons_cannot_be_empty(self):
        self.form_input['interval_between_lessons'] = None
        form = RequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_duration_of_lessons_can_accept_30_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.THIRTY_MINUTES
        form = RequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_can_accept_45_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.FOURTY_FIVE_MINUTES
        form = RequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_can_accept_60_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.SIXTY_MINUTES
        form = RequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_cannot_be_empty(self):
        self.form_input['duration_of_lessons'] = None
        form = RequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_further_information_cannot_be_empty(self):
        self.form_input['further_information'] = ''
        form = RequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_further_information_can_be_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 500
        form = RequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_further_information_cannot_be_over_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 501
        form = RequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_set_read_only(self):
        form = RequestViewForm(data=self.form_input)
        form.set_read_only()
        self.assertTrue(form.fields['availability'].disabled)
        self.assertTrue(form.fields['number_of_lessons'].disabled)
        self.assertTrue(form.fields['interval_between_lessons'].disabled)
        self.assertTrue(form.fields['duration_of_lessons'].disabled)
        self.assertTrue(form.fields['further_information'].disabled)

    # Todo: add form_must_save_properly()

    #This test is broken, the availability part.

    # def test_form_must_save_properly(self):
    #     # Need to create a request object, the form should be able to edit this request object and save it.
    #
    #     form = RequestForm(data=self.form_input)
    #     self.assertTrue(form.is_valid())
    #     form_availability = form.cleaned_data.get('availability')
    #     form_number_of_lessons = form.cleaned_data.get('number_of_lessons')
    #     form_interval_between_lessons = form.cleaned_data.get('interval_between_lessons')
    #     form_duration_of_lessons = form.cleaned_data.get('duration_of_lessons')
    #     form_further_information = form.cleaned_data.get('further_information')
    #     Request.objects.create(
    #         user_id=1,
    #         relation_id=2,
    #         date=timezone.datetime.now(tz=timezone.utc),
    #         number_of_lessons=form_number_of_lessons,
    #         interval_between_lessons=form_interval_between_lessons,
    #         duration_of_lessons=form_duration_of_lessons,
    #         further_information=form_further_information
    #     ).availability.set(form_availability)
    #
    #     request = Request.objects.get(id=1)
    #     #daysOfTheWeek = DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.MONDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY) # Testing
    #     #request.availability.set(daysOfTheWeek) #Testing
    #     #print(request.availability) # This prints out lessons.DayofTheWeek.None
    #     form = RequestForm(instance=request, data=self.form_input) #This works right?, the save function cannot find the instance id of this request pbject?
    #     before_count = Request.objects.count()
    #     form.save()
    #     after_count = RequestForm.objects.count()
    #     self.assertEqual(after_count, before_count)
    #
    #     self.assertEqual(request.date, self.currentDate)
    #     self.assertEqual(request.number_of_lessons, 1)
    #     self.assertEqual(request.interval_between_lessons, Request.IntervalBetweenLessons.ONE_WEEK)
    #     self.assertEqual(request.duration_of_lessons, Request.LessonDuration.THIRTY_MINUTES)
    #     self.assertEqual(request.further_information, 'Some information')
    #     self.assertTrue(request.availability, form_availability)


