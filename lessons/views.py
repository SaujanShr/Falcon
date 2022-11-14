from django.shortcuts import render, redirect
from .models import Request
from .forms import RequestViewForm, LogInForm, TransactionSubmitForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .decorators import login_prohibited, allowed_groups
from django.conf import settings

@login_required
@allowed_groups(["Student"])
def student_page(request):
    requests = Request.objects.filter(user =request.user.id)
    return render(request, 'student_page.html', {'requests':requests})

@login_required
@allowed_groups(["Student"])
def request_view(request):
    if request.method == 'GET':
        this_request = Request.objects.get(date=request.GET['date'])
        form = RequestViewForm(
            initial={
                'date':this_request.date,
                'availability':this_request.availability.all(),
                'number_of_lessons':this_request.number_of_lessons,
                'interval_between_lessons':this_request.interval_between_lessons,
                'duration_of_lessons':this_request.duration_of_lessons,
                'further_information':this_request.further_information,
                'fulfilled':this_request.fulfilled
                }
            )
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