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
    path('admin/', admin.site.urls),
    path('student_page/', views.student_page, name='student_page'),
    path('request_list/', views.request_list, name='request_list'),
    path('request_view/', views.request_view, name='request_view'),
    path('new_request_view/', views.new_request_view, name='new_request_view'),
    path('log_in/', views.log_in, name='log_in'),
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('test_view/', views.test_redirect_view, name='redirect'),
    path('transactions/admin', views.transaction_admin_view, name='transaction_admin_view'),
    path('transactions/admin/submit', views.transaction_admin_view, name='transaction_admin_view'),
    path('transactions/admin/view', views.transaction_list_admin, name='transaction_list_admin'),
    path('transactions/student', views.transaction_list_student, name='transaction_list_student'),
    path('balance/admin', views.balance_list_admin, name='balance_list_admin'),
    path('admin_view_requests_and_bookings/', views.admin_bookings_requests_view, name='admin_request_view'),
    path('student_page/terms', views.student_term_view, name='student_term_view'),
    path('admin_term_view', views.admin_term_view, name='admin_term_view'),
    path('term_view', views.term_view, name='term_view'),
    path('profile/', views.profile, name='profile'),
    path('change_password/', views.password, name='change_password'),
    path('log_out/', views.log_out, name='log_out'),
]
