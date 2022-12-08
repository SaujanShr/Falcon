import datetime

from django.test import TestCase
from django import forms
from lessons.models import User, Student, DayOfTheWeek, SchoolTerm, Booking, Invoice
from lessons.forms import BookingEditForm
from lessons.tests.helpers import create_days_of_the_week, create_user_groups

class BookingEditFormTestCase(TestCase):
    """Unit tests for the BookingEditForm form"""
    
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/default_terms']
    
    def setUp(self):
        create_user_groups()
        create_days_of_the_week()
        self.user = User.objects.all()[0]
        Student.objects.create(user=self.user)
        
        self.form_input = {
            'day_of_the_week':DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.MONDAY),
            'time_of_the_day':'00:00:00',
            'teacher':'Sam Harry',
            'start_date':'2011-10-10',
            'end_date':'2011-12-10',
            'duration_of_lessons':Booking.LessonDuration.THIRTY_MINUTES,
            'interval_between_lessons':Booking.IntervalBetweenLessons.ONE_WEEK,
            'number_of_lessons':1,
            'further_information':'Some informations',
            'hourly_cost':5.0
        }

        i1 = Invoice(
            invoice_number="0001-002",
            student=Student.objects.get(user__email="johndoe@email.com"),
            full_amount=300,
            paid_amount=299,
            fully_paid=False
        )
        i1.save()

        self.booking1 = Booking.objects.create(
            user=User.objects.get(email="johndoe@email.com"),
            relation_id=1,
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
        
    def _assert_form_is_valid(self):
        form = BookingEditForm(data=self.form_input)
        self.assertTrue(form.is_valid())
        
    def _assert_form_is_invalid(self):
        form = BookingEditForm(data=self.form_input)
        self.assertFalse(form.is_valid())
        
    def test_form_has_necessary_fields(self):
        form = BookingEditForm()
        self.assertIn('day_of_the_week', form.fields)
        self.assertTrue(isinstance(form.fields['day_of_the_week'], forms.ModelChoiceField))
        self.assertIn('time_of_the_day', form.fields)
        self.assertTrue(isinstance(form.fields['time_of_the_day'], forms.TimeField))
        self.assertIn('teacher', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertTrue(isinstance(form.fields['start_date'], forms.DateField))
        self.assertIn('end_date', form.fields)
        self.assertTrue(isinstance(form.fields['end_date'], forms.DateField))
        self.assertIn('duration_of_lessons', form.fields)
        self.assertIn('interval_between_lessons', form.fields)
        self.assertIn('number_of_lessons', form.fields)
        self.assertIn('further_information', form.fields)
        self.assertIn('hourly_cost', form.fields)
    
    def test_day_of_the_week_cannot_be_blank(self):
        self.form_input['day_of_the_week'] = ''
        self._assert_form_is_invalid()
        
    def test_day_of_the_week_can_hold_a_day(self):
        self.form_input['day_of_the_week'] = DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.FRIDAY)
        self._assert_form_is_valid()
        
    def test_time_of_day_cannot_hold_a_non_time_value(self):
        self.form_input['time_of_the_day'] = ''
        self._assert_form_is_invalid()
        self.form_input['time_of_the_day'] = '999:9'
        self._assert_form_is_invalid()
        self.form_input['time_of_the_day'] = '9999'
        self._assert_form_is_invalid()
        self.form_input['time_of_the_day'] = '-23:23'
    
    def test_time_of_day_cannot_be_over_the_24_hour_clock(self):
        self.form_input['time_of_the_day'] = '24:00:00'
        self._assert_form_is_invalid()
        
    def test_time_of_day_can_be_just_below_24_hours(self):
        self.form_input['time_of_the_day'] = '23:59:59'
        self._assert_form_is_valid()
        
    def test_teacher_cannot_be_blank(self):
        self.form_input['teacher'] = ''
        self._assert_form_is_invalid()
        
    def test_teacher_cannot_contain_over_100_characters(self):
        self.form_input['teacher'] = 'x' * 101
        self._assert_form_is_invalid()
        
    def test_teacher_can_contain_100_characters(self):
        self.form_input['teacher'] = 'x' * 100
        self._assert_form_is_valid()
        
    def test_start_date_cannot_hold_a_non_date_value(self):
        self.form_input['start_date'] = ''
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '99-99'
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '12:00'
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '20221010'
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '202210-10'
        self._assert_form_is_invalid()
        
    def test_end_date_cannot_hold_a_non_date_value(self):
        self.form_input['start_date'] = ''
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '99-99'
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '12:00'
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '20221010'
        self._assert_form_is_invalid()
        self.form_input['start_date'] = '202210-10'
        self._assert_form_is_invalid()
        
    def test_start_date_cannot_be_after_end_date(self):
        self.form_input['end_date'] = '0000-00-00'
        self._assert_form_is_invalid()
        
    def test_duration_of_lessons_cannot_be_blank(self):
        self.form_input['duration_of_lessons'] = ''
        self._assert_form_is_invalid()
        
    def test_interval_between_lessons_cannot_be_blank(self):
        self.form_input['interval_between_lessons'] = ''
        self._assert_form_is_invalid()
    
    def test_number_of_lessons_cannot_be_blank(self):
        self.form_input['number_of_lessons'] = ''
        self._assert_form_is_invalid()
    
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
    
    def test_further_information_cannot_be_blank(self):
        self.form_input['further_information'] = ''
        self._assert_form_is_invalid()
    
    def test_further_information_cannot_contain_over_500_characters(self):
        self.form_input['further_information'] = 'x' * 501
        self._assert_form_is_invalid()
    
    def test_further_information_may_contain_500_characters(self):
        self.form_input['further_information'] = 'x' * 500
        self._assert_form_is_valid()
    
    def test_hourly_cost_must_not_be_blank(self):
        self.form_input['hourly_cost'] = ''
        self._assert_form_is_invalid()
        
    def test_read_only(self):
        booking = BookingEditForm(data=self.form_input)
        booking.set_read_only()
        
        self.assertTrue(booking.fields['day_of_the_week'].disabled)
        self.assertTrue(booking.fields['time_of_the_day'].disabled)
        self.assertTrue(booking.fields['teacher'].disabled)
        self.assertTrue(booking.fields['start_date'].disabled)
        self.assertTrue(booking.fields['end_date'].disabled)
        self.assertTrue(booking.fields['duration_of_lessons'].disabled)
        self.assertTrue(booking.fields['interval_between_lessons'].disabled)
        self.assertTrue(booking.fields['number_of_lessons'].disabled)
        self.assertTrue(booking.fields['further_information'].disabled)
        self.assertTrue(booking.fields['hourly_cost'].disabled)
        
    def test_form_must_save_properly(self):
        Invoice.objects.create(
            invoice_number='0000-000',
            student=Student.objects.all()[0],
            full_amount=50,
            paid_amount=0
        )
        booking = Booking.objects.create(
            invoice = Invoice.objects.get(invoice_number='0000-000'),
            term_id = SchoolTerm.objects.all()[0],
            day_of_the_week = DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.SATURDAY),
            time_of_the_day = '00:11',
            user=self.user,
            relation_id=-1,
            teacher='John Smiggens',
            start_date='2000-10-10',
            end_date='2001-10-10',
            duration_of_lessons = Booking.LessonDuration.FORTY_FIVE_MINUTES,
            interval_between_lessons = Booking.IntervalBetweenLessons.ONE_WEEK,
            number_of_lessons = 3,
            further_information = 'Other information'
        )
        
        form = BookingEditForm(instance_id=booking.id, data=self.form_input)
        before_count = Booking.objects.count()
        booking = form.save()
        after_count = Booking.objects.count()
        
        self.assertEqual(before_count, after_count)
        
        self.assertEqual(booking.day_of_the_week, self.form_input['day_of_the_week'])
        self.assertEqual(str(booking.time_of_the_day), self.form_input['time_of_the_day'])
        self.assertEqual(booking.teacher, self.form_input['teacher'])
        self.assertEqual(str(booking.start_date), self.form_input['start_date'])
        self.assertEqual(str(booking.end_date), self.form_input['end_date'])
        self.assertEqual(booking.duration_of_lessons, self.form_input['duration_of_lessons'])
        self.assertEqual(booking.interval_between_lessons, self.form_input['interval_between_lessons'])
        self.assertEqual(booking.number_of_lessons, self.form_input['number_of_lessons'])
        self.assertEqual(booking.further_information, self.form_input['further_information'])

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
            'start_date': (SchoolTerm.objects.all()[0].end_date + datetime.timedelta(days=1)),
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
