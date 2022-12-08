from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Child, Student
from lessons.tests.helpers import create_user_groups

class ChildDashboardPageTestCase(TestCase):
    '''Unit test for the Child Page view'''
    
    fixtures = ['lessons/tests/fixtures/default_user.json','lessons/tests/fixtures/other_users.json']
    
    def setUp(self):
        create_user_groups()
        self.user1 = User.objects.all()[0]
        self.user2 = User.objects.all()[1]
        Student(user=self.user1).save()
        Student(user=self.user2).save()
        
        self.child = Child.objects.create(
            parent=self.user1,
            first_name='Joe',
            last_name='Swanson'
        )
        self.url = f'{reverse("child_page")}?relation_id={self.child.id}'
    
    def test_child_page_url(self):
        self.assertEqual(self.url, '/child_page/?relation_id=1')
    
    def test_non_parent_user_is_redirected(self):
        self.client.login(email=self.user2.email, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('children_list'), status_code=302, target_status_code=200)
    
    def test_child_idname_object(self):
        self.client.login(email=self.user1.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'child_page.html')
        
        child_idname = response.context['child']
        self.assertEqual({
            'id':self.child.id, 
            'name':f'{self.child.first_name} {self.child.last_name}'
            },
            child_idname)
        
    def test_user_balance(self):
        self.client.login(email=self.user1.email, password='Password123')
        student = Student.objects.get(user=self.user1)
        student.balance = 123
        student.save()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'child_page.html')
        
        balance = response.context['balance']
        self.assertEqual(balance, 123)
    
    def test_requests_button_redirects_to_child_request_list(self):
        self.client.login(email=self.user1.email, password='Password123')
        
        self.url = self.url + '&requests=1'
        response = self.client.get(self.url, follow=True)
        redirect_url = f'{reverse("child_request_list")}?relation_id={self.child.id}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_lessons_button_redirects_to_child_lesson_list(self):
        self.client.login(email=self.user1.email, password='Password123')
        
        self.url = self.url + '&lessons=1'
        response = self.client.get(self.url, follow=True)
        redirect_url = f'{reverse("lesson_list_child")}?relation_id={self.child.id}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_bookings_button_redirects_to_child_booking_list(self):
        self.client.login(email=self.user1.email, password='Password123')
        
        self.url = self.url + '&bookings=1'
        response = self.client.get(self.url, follow=True)
        redirect_url = f'{reverse("child_booking_list")}?relation_id={self.child.id}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    def test_return_button_returns_to_children_page(self):
        self.client.login(email=self.user1.email, password='Password123')
        
        self.url = self.url + '&return=1'
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse("children_list")
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        
    