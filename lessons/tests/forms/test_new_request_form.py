"""Unit tests of the new requests form."""
from django.test import TestCase
from lessons.forms import NewRequestViewForm
from lessons.models import DayOfTheWeek, Request
from lessons.models import User
from django.utils import timezone

class LogInFormTestCase(TestCase):
    def setUp(self):
        DayOfTheWeek.objects.create(order=0, day=DayOfTheWeek.Day.MONDAY)
        DayOfTheWeek.objects.create(order=1, day=DayOfTheWeek.Day.TUESDAY)
        DayOfTheWeek.objects.create(order=2, day=DayOfTheWeek.Day.WEDNESDAY)
        DayOfTheWeek.objects.create(order=3, day=DayOfTheWeek.Day.THURSDAY)
        DayOfTheWeek.objects.create(order=4, day=DayOfTheWeek.Day.FRIDAY)
        DayOfTheWeek.objects.create(order=5, day=DayOfTheWeek.Day.SATURDAY)
        DayOfTheWeek.objects.create(order=6, day=DayOfTheWeek.Day.SUNDAY)

        availability = DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY)
        number_of_lessons = 1
        interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK
        duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES
        further_information = 'Some information'
        self.form_input = {
            'availability': availability,
            'number_of_lessons': number_of_lessons,
            'interval_between_lessons': interval_between_lessons,
            'duration_of_lessons': duration_of_lessons,
            'further_information': further_information,
        }

    def test_valid_sign_up_form(self):
        form = NewRequestViewForm(data=self.form_input)
        # print(form) #TESTING
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = NewRequestViewForm()
        self.assertIn('availability', form.fields)

        self.assertIn('number_of_lessons', form.fields)

        self.assertIn('interval_between_lessons', form.fields)

        self.assertIn('duration_of_lessons', form.fields)

        self.assertIn('further_information', form.fields)

    def test_availability_cannot_accept_no_choices(self):
        self.form_input['availability'] = None
        form = NewRequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_availability_can_accept_multiple_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.THURSDAY)
        form = NewRequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_availability_can_accept_all_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.MONDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.THURSDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.FRIDAY)
        form = NewRequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_number_of_lessons_can_be_1(self):
        self.form_input['number_of_lessons'] = 1
        form = NewRequestViewForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_number_of_lessons_can_be_2(self):
        self.form_input['number_of_lessons'] = 2
        form = NewRequestViewForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_number_of_lessons_can_only_be_1_or_2(self):
        self.form_input['number_of_lessons'] = 3
        form = NewRequestViewForm(data=self.form_input)
        lessonsGreaterThan2 = form.is_valid()

        self.form_input['number_of_lessons'] = 0
        form = NewRequestViewForm(data=self.form_input)
        lessonsLessThan1 = form.is_valid()

        self.assertFalse(lessonsGreaterThan2 and lessonsLessThan1)

    def test_interval_between_lessons_cannot_be_empty(self):
        self.form_input['interval_between_lessons'] = None
        form = NewRequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_duration_of_lessons_can_accept_30_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.THIRTY_MINUTES
        form = NewRequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_can_accept_45_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.FOURTY_FIVE_MINUTES
        form = NewRequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_can_accept_60_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.SIXTY_MINUTES
        form = NewRequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_cannot_be_empty(self):
        self.form_input['duration_of_lessons'] = None
        form = NewRequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_further_information_cannot_be_empty(self):
        self.form_input['further_information'] = ''
        form = NewRequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_further_information_can_be_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 500
        form = NewRequestViewForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_further_information_cannot_be_over_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 501
        form = NewRequestViewForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Not sure how to do this.

    # def test_form_must_save_correctly(self):
    #     form = NewRequestViewForm(data=self.form_input)
    #     form.is_valid()
    #     form_availability = form.cleaned_data.get('availability')
    #     form_number_of_lessons = form.cleaned_data.get('number_of_lessons')
    #     form_interval_between_lessons = form.cleaned_data.get('interval_between_lessons')
    #     form_duration_of_lessons = form.cleaned_data.get('duration_of_lessons')
    #     form_further_information = form.cleaned_data.get('further_information')
    #     Request.objects.create(
    #         user=User.objects.create_user(
    #             email='email@email.com',
    #             password='Password123'
    #         ),
    #         date=timezone.datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
    #         #availability=form_availability,
    #         number_of_lessons=form_number_of_lessons,
    #         interval_between_lessons=form_interval_between_lessons,
    #         duration_of_lessons=form_duration_of_lessons,
    #         further_information=form_further_information
    #     ).availability.set(form_availability)
    #     before_count = Request.objects.count()
    #     form.save()
    #     after_count = Request.objects.count()
    #     self.assertEqual(after_count, before_count + 1)  # Check that the Request count has increased by 1