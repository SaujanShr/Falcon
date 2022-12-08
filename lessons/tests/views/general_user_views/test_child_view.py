"""Unit test for the ChildView view"""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import ChildEditForm
from lessons.models import User, Child, Student
from lessons.tests.helpers import create_user_groups, HandleGroups


class ChildViewTestCase(TestCase):
    """Unit test for the ChildView view"""
    
    fixtures = ['lessons/tests/fixtures/default_user.json', 'lessons/tests/fixtures/other_users.json']
    
    def setUp(self):
        create_user_groups()
        self.user1 = User.objects.all()[0]
        self.user2 = User.objects.all()[1]
        Student(user=self.user1).save()
        Student(user=self.user2).save()
        
        self.child = Child.objects.create(
            parent = self.user1,
            first_name = 'Bob',
            last_name = 'Harry'
        )
        self.form_input = {
            'relation_id': self.child.id,
            'first_name': 'Jerry',
            'last_name': 'Garry'
        }
        self.url = f'{reverse("child_view")}?relation_id={self.child.id}'
        
    def test_child_view_url(self):
        self.assertEqual(self.url, '/child_view/?relation_id=1')
        
    def test_redirect_if_admin(self):
        HandleGroups.set_default_user_to_admin()
        self.client.login(email='johndoe@email.com', password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('admin_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_non_parent_user_is_redirected(self):
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('children_list'), status_code=302, target_status_code=200)
    
    def test_successful_child_edit(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        self.url = f'{reverse("child_view")}'
        self.form_input['update'] = True
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse("children_list")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'children_list.html')
        self.assertEqual(Child.objects.count(), 1)
        
        child = Child.objects.all()[0]
        self.assertEqual(child.first_name, self.form_input['first_name'])
        self.assertEqual(child.last_name, self.form_input['last_name'])
    
    def test_blank_first_name(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        self.form_input['first_name'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        form = response.context['form']
        self.assertTrue(isinstance(form, ChildEditForm))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'child_view.html')
        self.assertEqual(Child.objects.count(), 1)
    
    def test_blank_last_name(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        self.form_input['last_name'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        form = response.context['form']
        self.assertTrue(isinstance(form, ChildEditForm))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'child_view.html')
        self.assertEqual(Child.objects.count(), 1)
        
    def test_successful_child_delete(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        self.url = f'{reverse("child_view")}'
        self.form_input['delete'] = True
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse("children_list")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'children_list.html')
        self.assertEqual(Child.objects.count(), 0)
        
    def test_return_redirects_to_children_list_on_return_button(self):
        self.client.login(email='johndoe@email.com', password='Password123')
        self.url = f'{reverse("child_view")}'
        self.form_input['return'] = True
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse("children_list")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'children_list.html')
        self.assertEqual(Child.objects.count(), 1)