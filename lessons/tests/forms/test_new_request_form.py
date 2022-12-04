"""Unit tests of the new requests form."""
from django.utils import timezone
from django.test import TestCase
from lessons.forms import NewRequestForm
from lessons.models import DayOfTheWeek, Request, User
from lessons.tests.helpers import create_user_groups, create_days_of_the_week


class NewRequestFormTestCase(TestCase):
    """Unit tests of the new requests form."""
    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        create_user_groups()
        create_days_of_the_week()

        self.user = User.objects.get(email="johndoe@email.com")

        # Create form inputs
        student_name = 'John Doe'
        availability = DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY)
        number_of_lessons = 1
        interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK
        duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES
        further_information = 'Some information'

        # Initialise form input
        self.form_input = {
            'student_name': student_name,
            'availability': availability,
            'number_of_lessons': number_of_lessons,
            'interval_between_lessons': interval_between_lessons,
            'duration_of_lessons': duration_of_lessons,
            'further_information': further_information,
        }

    def test_valid_sign_up_form(self):
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = NewRequestForm()
        self.assertIn('availability', form.fields)

        self.assertIn('number_of_lessons', form.fields)

        self.assertIn('interval_between_lessons', form.fields)

        self.assertIn('duration_of_lessons', form.fields)

        self.assertIn('further_information', form.fields)

    def test_availability_cannot_accept_no_choices(self):
        self.form_input['availability'] = None
        form = NewRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_availability_can_accept_multiple_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.THURSDAY)
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_availability_can_accept_all_choices(self):
        self.form_input['availability'] = DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.MONDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.TUESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.WEDNESDAY), DayOfTheWeek.objects.get(
            day=DayOfTheWeek.Day.THURSDAY), DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.FRIDAY)
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_number_of_lessons_cannot_be_empty(self):
        self.form_input['number_of_lessons'] = None
        form = NewRequestForm(data=self.form_input)

        self.assertFalse(form.is_valid())

    def test_number_of_lessons_can_be_1(self):
        self.form_input['number_of_lessons'] = 1
        form = NewRequestForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_number_of_lessons_can_greater_than_1(self):
        self.form_input['number_of_lessons'] = 2
        form = NewRequestForm(data=self.form_input)

        self.assertTrue(form.is_valid())

    def test_number_of_lessons_cannot_be_less_than_1(self):
        self.form_input['number_of_lessons'] = 0
        form = NewRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_number_of_lessons_can_be_max_int_for_SQLite_DB(self):
        self.form_input['number_of_lessons'] = 9223372036854775807
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_number_of_lessons_cannot_be_greater_than_max_int_for_SQLite_DB(self):
        self.form_input['number_of_lessons'] = 92233720368547758071
        form = NewRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_interval_between_lessons_cannot_be_empty(self):
        self.form_input['interval_between_lessons'] = None
        form = NewRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_duration_of_lessons_can_accept_30_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.THIRTY_MINUTES
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_can_accept_45_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.FOURTY_FIVE_MINUTES
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_can_accept_60_minutes(self):
        self.form_input['duration_of_lessons'] = Request.LessonDuration.SIXTY_MINUTES
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_duration_of_lessons_cannot_be_empty(self):
        self.form_input['duration_of_lessons'] = None
        form = NewRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_further_information_cannot_be_empty(self):
        self.form_input['further_information'] = ''
        form = NewRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_further_information_can_be_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 500
        form = NewRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_further_information_cannot_be_over_500_characters_long(self):
        self.form_input['further_information'] = 'a' * 501
        form = NewRequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    # Not sure how to do this.
    # django.db.utils.IntegrityError: NOT NULL constraint failed: lessons_request.user_id

    # def test_form_must_save_correctly(self):
    #     form = NewRequestViewForm(data=self.form_input)
    #     form.is_valid()
    #     form_availability = form.cleaned_data.get('availability')
    #     form_number_of_lessons = form.cleaned_data.get('number_of_lessons')
    #     form_interval_between_lessons = form.cleaned_data.get('interval_between_lessons')
    #     form_duration_of_lessons = form.cleaned_data.get('duration_of_lessons')
    #     form_further_information = form.cleaned_data.get('further_information')
    #     Request.objects.create(
    #         #replace with fixture
    #         # user=User.objects.create_user(
    #         #     first_name="john",
    #         #     last_name="doe",
    #         #     email='email@email.com',
    #         #     password='Password123'
    #         # ),
    #         date=timezone.datetime.now(tz=timezone.utc),
    #         #availability=form_availability,
    #         number_of_lessons=form_number_of_lessons,
    #         interval_between_lessons=form_interval_between_lessons,
    #         duration_of_lessons=form_duration_of_lessons,
    #         further_information=form_further_information
    #     ).availability.set(form_availability)
    #
    #     before_count = Request.objects.count()
    #     form.save(self.user)
    #     after_count = Request.objects.count()
    #     self.assertEqual(after_count, before_count + 1)  # Check that the Request count has increased by 1
