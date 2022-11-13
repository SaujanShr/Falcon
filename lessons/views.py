from django.shortcuts import render, redirect
from .models import Request
from .forms import RequestViewForm, LogInForm, SignUpForm
from django.contrib import messages
from django.contrib.auth import authenticate, login


def student_page(request):
    requests = Request.objects.all()
    return render(request, 'student_page.html', {'requests': requests})


def request_view(request):
    if request.method == 'GET':
        this_request = Request.objects.get(date=request.GET['date'])
        form = RequestViewForm(
            initial={
                'date': this_request.date,
                'availability': this_request.availability.all(),
                'number_of_lessons': this_request.number_of_lessons,
                'interval_between_lessons': this_request.interval_between_lessons,
                'duration_of_lessons': this_request.duration_of_lessons,
                'further_information': this_request.further_information,
                'fulfilled': this_request.fulfilled
            }
        )
        return render(request, 'request_view.html', {'form': form})


def home(request):
    return render(request, 'home.html')


def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('feed')
        # Credentials are incorrect
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form})


def sign_up(request):
    form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})
