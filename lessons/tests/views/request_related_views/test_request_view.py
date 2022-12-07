"""Tests of the request view."""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestEditForm
from lessons.models import Request, DayOfTheWeek
from lessons.tests.helpers import create_user_groups, HandleGroups, create_days_of_the_week
from django.utils import timezone


class RequestViewTestCase(TestCase):
    """Tests of the request view"""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_student()
        self.client.login(email="johndoe@email.com", password="Password123")

        self.url = reverse('request_view')

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
        # print(self.request)
        self.request = Request.objects.get(id=1)

    def test_request_url(self):
        self.assertEqual(self.url, '/request_view/')

    def test_get_request_view(self):
        response = self.client.get(self.url + "?request_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RequestEditForm))
        self.assertFalse(form.is_bound)

    def test_get_request_of_another_student_redirects(self):
        self.client.login(email="janedoe@email.com", password="Password123")
        response = self.client.get(self.url + "?request_id=1", follow=True)
        response_url = reverse('student_page')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_page.html')

    def test_read_only_due_to_fulfilled_request(self):
        payload = {'request_id': 2, 'relation_id': -1}
        response = self.client.get(self.url + "?request_id=2", payload, follow=True)
        self.assertTemplateUsed(response, 'request_view.html')

        form = response.context['form']
        self.assertTrue(form.fields['date'].disabled)
        self.assertTrue(form.fields['availability'].disabled)
        self.assertTrue(form.fields['number_of_lessons'].disabled)
        self.assertTrue(form.fields['interval_between_lessons'].disabled)
        self.assertTrue(form.fields['duration_of_lessons'].disabled)
        self.assertTrue(form.fields['further_information'].disabled)

    def test_successful_request_redirect_on_return_button(self):
        payload = {'request_id': 1, 'relation_id': -1, 'full_name': 'john doe', 'return': ' '}
        response = self.client.post(self.url + "?request_id=1", payload, follow=True)
        response_url = reverse('request_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'request_list.html')

    def test_successful_request_deletion_with_delete_button(self):
        payload = {'request_id': 1, 'relation_id': -1, 'full_name': 'john doe', 'delete': ' '}
        before_count = Request.objects.count()
        response = self.client.post(self.url + "?request_id=1", payload, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(before_count, after_count + 1)
        response_url = reverse('request_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'request_list.html')

    def test_successful_request_edit(self):
        payload = {'request_id': 1, 'relation_id': -1, 'full_name': 'john doe', 'availability': '1',
                   'number_of_lessons': '2', 'interval_between_lessons': '7', 'duration_of_lessons': '30',
                   'further_information': 'None', 'update': ' '}
        self.form_input['number_of_lessons'] = 1
        before_count = Request.objects.count()
        response = self.client.post(self.url + "?request_id=1", payload, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('request_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'request_list.html')

    def test_unsuccessful_request_edit(self):
        # self.form_input['request_id'] = 1
        payload = {'request_id': 1, 'relation_id': -1, 'full_name': 'john doe', 'availability': '-1',
                   'number_of_lessons': '2', 'interval_between_lessons': '7', 'duration_of_lessons': '30',
                   'further_information': 'None', 'update': ' '}
        self.form_input['number_of_lessons'] = 1
        before_count = Request.objects.count()
        response = self.client.post(self.url + "?request_id=1", payload, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_view.html')