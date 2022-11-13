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
    path('request_view/', views.request_view, name='request_view'),
    path('new_request/', views.request_view, name='request_view'),
    path('',views.home,name='home'),
    path('log_in/',views.log_in,name='log_in'),
    path('sign_up/',views.home,name='sign_up'),
    path('test_view/',views.test_redirect_view,name='redirect')
]
