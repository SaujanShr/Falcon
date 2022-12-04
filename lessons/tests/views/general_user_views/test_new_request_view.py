"""Tests of the new-request view."""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import NewRequestForm
from lessons.models import Request
from lessons.tests.helpers import create_user_groups, HandleGroups, create_days_of_the_week


class NewRequestViewTestCase(TestCase):
    """Tests of the new-request view"""
    fixtures = ['lessons/tests/fixtures/default_user.json']

    def setUp(self):
        create_user_groups()
        HandleGroups.set_default_user_to_student()
        self.client.login(email="johndoe@email.com", password="Password123")

        self.url = reverse('new_request_view')

        create_days_of_the_week()
        
        student_name = 'Me'
        availability = 1
        number_of_lessons = 1
        interval_between_lessons = Request.IntervalBetweenLessons.ONE_WEEK
        duration_of_lessons = Request.LessonDuration.THIRTY_MINUTES
        further_information = 'Some information'
        self.form_input = {
            'student_name': student_name,
            'availability': availability,
            'number_of_lessons': number_of_lessons,
            'interval_between_lessons': interval_between_lessons,
            'duration_of_lessons': duration_of_lessons,
            'further_information': further_information,
        }

    def test_new_request_url(self):
        self.assertEqual(self.url, '/new_request_view/')

    def test_get_new_request_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_request_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewRequestForm))
        self.assertFalse(form.is_bound)

    def test_unsuccessful_new_request(self):
        self.form_input['number_of_lessons'] = -1
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_request_view.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, NewRequestForm))
        #self.assertTrue(form.is_bound)

    def test_successful_new_request(self):
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count + 1)  # Check that the Request count has increased by 1
        response_url = reverse('request_list')
        self.assertRedirects(response, response_url, status_code=302,
                             target_status_code=200)
        self.assertTemplateUsed(response, 'request_list.html')

        request = Request.objects.all()[:1].get()  # Gets the first item in Requests as there is only one request object in the test database. This is kind of bad. Need to change?
        #self.assertEqual(request.availability, DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.MONDAY))  # This doesn't work
        self.assertEqual(request.number_of_lessons, 1)
        self.assertEqual(request.interval_between_lessons, Request.IntervalBetweenLessons.ONE_WEEK)
        self.assertEqual(request.duration_of_lessons, Request.LessonDuration.THIRTY_MINUTES)
        self.assertEqual(request.further_information, 'Some information')
