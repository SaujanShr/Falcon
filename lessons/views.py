from django.shortcuts import render, redirect
from .models import Request
from .forms import RequestViewForm, LogInForm, TransactionSubmitForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .decorators import login_prohibited, allowed_groups
from django.conf import settings
from functions import *

@login_required
@allowed_groups(["Student"])
def student_page(request):
    return render(request, 'student_page.html')

@login_required
@allowed_groups(["Student"])
def request_list(request):
    if request.method == 'POST':
        data = request.POST
        if 'delete' in data:
            delete_request(data)
        elif 'edit' in data:
            if data.is_valid():
                update_request(data)
                
    user_requests = get_user_requests(request.user)
    return render(request, 'request_list.html', {'user_requests':user_requests})

@login_required
@allowed_groups(["Student"])
def request_view(request):
    data = request.GET
    form = get_request_view_form(data)
    return render(request, 'request_view.html', {'form':form})

@login_prohibited
def home(request):
    return render(request, 'home.html')

@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                if (user.groups.all()[0].name == 'Student'):
                    user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT
                elif (user.groups.all()[0].name == 'Admin'):
                    user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_ADMIN
                redirect_url = request.POST.get('next') or user_specific_redirect
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR,
                             "The credentials provided were invalid!")
    form = LogInForm()
    next = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next})

def sign_up(request):
    return render(request, 'home.html')

# THIS VIEW IS FOR TESTING PURPOSES, TO DELETE FOR LATER VERSIONS
@login_required
@allowed_groups(["Admin"])
def test_redirect_view(request):
    return render(request, 'test_redirect.html')

def transaction_admin_view(request):
    if request.method == 'POST':
        form = TransactionSubmitForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = TransactionSubmitForm()
    
    return render(request, 'transaction_admin_view.html', {'form' : form})