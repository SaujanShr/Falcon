"""Tests of the admin request list view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import Request, DayOfTheWeek
from lessons.tests.helpers import create_user_groups, HandleGroups, create_days_of_the_week
from django.utils import timezone


class AdminRequestListTestCase(TestCase):
    """Tests of the admin request list view"""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_admin()
        self.client.login(email="janedoe@email.com", password="Password123")

        self.url = reverse('admin_request_list')

        create_days_of_the_week()

        student_name = 'Me'
        availability = 1
        number_of_lessons = 1
        interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK
        duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES
        further_information = 'Some information'

        self.form_input = {
            'date': timezone.datetime.now(tz=timezone.utc),
            'student_name': student_name,
            'availability': availability,
            'number_of_lessons': number_of_lessons,
            'interval_between_lessons': interval_between_lessons,
            'duration_of_lessons': duration_of_lessons,
            'further_information': further_information,
        }

        Request.objects.create(
            user_id=1,
            relation_id=-1,
            date=timezone.datetime.now(tz=timezone.utc),
            number_of_lessons=number_of_lessons,
            interval_between_lessons=interval_between_lessons,
            duration_of_lessons=duration_of_lessons,
            further_information=further_information
        ).availability.add(DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY))

        Request.objects.create(
            user_id=1,
            relation_id=-1,
            date=timezone.datetime.now(tz=timezone.utc),
            number_of_lessons=number_of_lessons,
            interval_between_lessons=interval_between_lessons,
            duration_of_lessons=duration_of_lessons,
            further_information=further_information,
            fulfilled=True
        ).availability.add(DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY))
        self.request = Request.objects.get(id=1)

    def test_request_url(self):
        self.assertEqual(self.url, '/admin_request_list/')

    def test_get_admin_request_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_request_list.html')

    def test_student_cannot_access_admin_request_list(self):
        self.client.login(email="johndoe@email.com", password="Password123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

