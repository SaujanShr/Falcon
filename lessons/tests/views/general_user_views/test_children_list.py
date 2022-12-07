"""Unit tests of the children list view."""
from django.test import TestCase
from lessons.models import User, Child
from lessons.tests.helpers import create_user_groups, HandleGroups
from django.urls import reverse


class ChildrenListTestCase(TestCase):
    """Unit tests of the children list view."""
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']

    def setUp(self):
        create_user_groups()
        HandleGroups.set_default_user_to_student()
        HandleGroups.set_other_user_to_student()

        self.user = User.objects.get(email="johndoe@email.com")
        self.child1 = Child.objects.create(parent=self.user, first_name="Jeff", last_name="Doe")
        self.child2 = Child.objects.create(parent=self.user, first_name="Jill", last_name="Doe")
        self.child3 = Child.objects.create(parent=self.user, first_name="Jacob", last_name="Doe")

        self.url = reverse('children_list')
        self.client.login(email='johndoe@email.com', password='Password123')

    def test_lesson_list_url(self):
        self.assertEqual(self.url, '/children_list/')

    def test_get_children_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'children_list.html')
        children = response.context['children']
        self.assertTrue(children)
        self.assertTrue(isinstance(children, list))

    def test_children_list_displays_all_of_logged_in_users_children(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'children_list.html')
        children = response.context['children']

        self.assertTrue(children)

        parent = User.objects.get(email="johndoe@email.com")

        self.assertEqual(len(children), len(Child.objects.filter(parent=parent)))

    def test_children_list_displays_no_children_for_user_with_no_children(self):
        self.client.login(email='janedoe@email.com', password='Password123')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'children_list.html')
        children = response.context['children']

        self.assertEqual(len(children), 0)
