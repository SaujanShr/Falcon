from django.test import TestCase
from django.urls import reverse
from lessons.forms import NewChildForm
from lessons.models import User, Child, Student
from lessons.tests.helpers import create_user_groups, HandleGroups

class NewChildViewTestCase(TestCase):
    '''Unit test for the NewChildView view'''
    
    fixtures = ['lessons/tests/fixtures/default_user.json']
    
    def setUp(self):
        create_user_groups()
        self.user = User.objects.all()[0]
        Student(user=self.user).save()
        
        self.url = reverse('new_child_view')
        self.client.login(email='johndoe@email.com', password='Password123')
        
        self.form_input = {
            'first_name': 'Billy',
            'last_name': 'Herrington'
        }
    
    def test_new_child_view_url(self):
        self.assertEqual(self.url, '/new_child_view/')
    
    def test_redirect_if_admin(self):
        HandleGroups.set_default_user_to_admin()
        response = self.client.get(self.url)
        redirect_url = reverse('admin_page')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    def test_successful_new_child(self):
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('children_list')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'children_list.html')
        self.assertEqual(Child.objects.count(), 1)
        
        child = Child.objects.all()[0]
        self.assertEqual(child.first_name, self.form_input['first_name'])
        self.assertEqual(child.last_name, self.form_input['last_name'])
    
    def test_blank_first_name(self):
        self.form_input['first_name'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        form = response.context['form']
        self.assertTrue(isinstance(form, NewChildForm))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_child_view.html')
        self.assertEqual(Child.objects.count(), 0)
    
    def test_blank_last_name(self):
        self.form_input['last_name'] = ''
        response = self.client.post(self.url, self.form_input, follow=True)
        form = response.context['form']
        self.assertTrue(isinstance(form, NewChildForm))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_child_view.html')
        self.assertEqual(Child.objects.count(), 0)