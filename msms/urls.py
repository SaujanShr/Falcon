"""msms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('admin_user_list/', views.admin_user_list, name='admin_user_list'),
    path('student_page/', views.student_page, name='student_page'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('request_list/', views.request_list, name='request_list'),
    path('booking_list/', views.booking_list, name='booking_list'),
    path('booking_view/', views.booking_view, name='booking_view'),
    path('request_view/', views.request_view, name='request_view'),
    path('new_request_view/', views.new_request_view, name='new_request_view'),
    path('children_list/', views.children_list, name='children_list'),
    path('child_view/', views.child_view, name='child_view'),
    path('child_page/', views.child_page, name='child_page'),
    path('child_request_list/', views.child_request_list, name='child_request_list'),
    path('child_booking_list/', views.child_booking_list, name='child_booking_list'),
    path('new_child_view/', views.new_child_view, name='new_child_view'),
    path('lessons/admin', views.lesson_list_admin, name='lesson_list_admin'),
    path('lessons/student', views.lesson_list_student, name='lesson_list_student'),
    path('lessons/child', views.lesson_list_child, name='lesson_list_child'),
    path('log_in/', views.log_in, name='log_in'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('test_view/', views.test_redirect_view, name='redirect'),
    path('transactions/admin', views.transaction_admin_view, name='transaction_admin_view'),
    path('transactions/admin/submit', views.transaction_admin_view, name='transaction_admin_view'),
    path('transactions/admin/view', views.transaction_list_admin, name='transaction_list_admin'),
    path('transactions/student', views.transaction_list_student, name='transaction_list_student'),
    path('balance/admin', views.balance_list_admin, name='balance_list_admin'),
    path('invoice/admin', views.invoice_list_admin, name='invoice_list_admin'),
    path('invoice/student', views.invoice_list_student, name='invoice_list_student'),
    path('invoice/view', views.invoice_view, name='invoice_view'),
    path('admin_request_list/', views.admin_request_list, name='admin_request_list'),
    path('admin_booking_list/', views.admin_booking_list, name='admin_booking_list'),
    path('fulfil_request/', views.fulfil_request_view, name='fulfil_request'),
    path('profile/', views.profile, name='profile'),
    path('student_page/terms', views.student_term_view, name='student_term_view'),
    path('admin_term_view', views.admin_term_view, name='admin_term_view'),
    path('admin_term_view/new_term', views.new_term_view, name='new_term_view'),
    path('admin_term_view/delete_confirmation', views.term_deletion_confirmation_view, name='term_deletion_confirmation_view'),
    path('term_view', views.term_view, name='term_view'),
    path('profile/<int:user_id>', views.profile, name='profile'),
    path('change_password/', views.change_user_password, name='change_password'),
    path('log_out/', views.log_out, name='log_out'),
    path('create_admin_user/', views.create_admin_user,name='create_admin_user'),
    path('create_student_user/', views.create_student_user,name='create_student_user'),
    path('create_director_user/', views.create_director_user,name='create_director_user')
]
