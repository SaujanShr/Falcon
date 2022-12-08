"""Unit tests of the child request list view."""
from django.test import TestCase
from lessons.models import User, DayOfTheWeek, Child, Request
from lessons.tests.helpers import create_user_groups, create_days_of_the_week, HandleGroups
from django.urls import reverse
from django.utils import timezone


class ChildRequestListTestCase(TestCase):
    """Unit tests of the child request list view."""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        create_days_of_the_week()
        HandleGroups.set_default_user_to_student()

        self.user = User.objects.get(email="johndoe@email.com")
        self.child1 = Child.objects.create(parent=self.user, first_name="Jeff", last_name="Doe")
        self.child2 = Child.objects.create(parent=self.user, first_name="Jill", last_name="Doe")

        self.request1 = Request.objects.create(
            user_id=1,
            relation_id=1,
            date=timezone.datetime.now(tz=timezone.utc),
            number_of_lessons=1,
            interval_between_lessons=Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons=Request.LessonDuration.THIRTY_MINUTES,
            further_information="Further Info",
        ).availability.add(DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY))

        self.request2 = Request.objects.create(
            user_id=1,
            relation_id=1,
            date=timezone.datetime.now(tz=timezone.utc),
            number_of_lessons=1,
            interval_between_lessons=Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons=Request.LessonDuration.THIRTY_MINUTES,
            further_information="Further Info",
            fulfilled=True
        ).availability.add(DayOfTheWeek.objects.get(day=DayOfTheWeek.Day.TUESDAY))

        self.url = reverse('child_request_list')

        self.client.login(email='johndoe@email.com', password='Password123')

    def test_child_request_list_url(self):
        self.assertEqual(self.url, '/child_request_list/')

    def test_get_child_request_list(self):
        response = self.client.get(f"{self.url}?relation_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'child_request_list.html')
        child_requests = response.context['child_requests']
        self.assertTrue(child_requests)

    def test_child_request_list_displays_only_child_request_for_current_user(self):
        response = self.client.get(f"{self.url}?relation_id=1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'child_request_list.html')
        child_requests = response.context['child_requests']

        self.assertTrue(child_requests)

        parent = User.objects.get(email="johndoe@email.com")
        child_id = 1
        self.assertQuerysetEqual(child_requests, Request.objects.filter(user_id=parent.id).filter(relation_id=child_id).order_by('-id').order_by('-date'))

    def test_child_request_list_displays_no_requests_for_child_with_no_requests(self):
        response = self.client.get(f"{self.url}?relation_id=2")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'child_request_list.html')
        child_requests = response.context['child_requests']

        self.assertEqual(len(child_requests), 0)

    def test_child_request_list_redirects_on_non_existent_child(self):
        response = self.client.get(f"{self.url}?relation_id=100", follow=True)

        response_url = reverse('children_list')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'children_list.html')
