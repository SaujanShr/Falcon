from django.shortcuts import render, redirect
from .models import Request, Booking
from .forms import LogInForm, TransactionSubmitForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .decorators import login_prohibited, allowed_groups
from django.conf import settings
from .functions import *

@login_required
@allowed_groups(['Student'])
def student_page(request):
    return render(request, 'student_page.html')

@login_required
@allowed_groups(['Student'])
def request_list(request):
    if request.method == 'POST':
        data = request.POST
        if 'delete' in data:
            delete_request(data)
        elif 'update' in data:
            update_request(data)
    
    user_requests = get_user_requests(request.user)
    return render(request, 'request_list.html', {'user_requests':user_requests})
        

@login_required
@allowed_groups(['Student'])
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

#@login_required
#@allowed_groups(["Admin"])
def admin_bookings_requests_view(request):
    if request.method == 'GET':

        """
        booking1 = Booking.objects.create(
            student=User.objects.create_user(
                email='jane2doe@gmail.com',
                password="password"
            ),
            invoice_id="0002-001",
            time_of_the_day="8:00",
            teacher="Mr Smith",
            number_of_lessons=15,
            start_date="2022-11-22",
            duration_of_lessons=Booking.LessonDuration.THIRTY_MINUTES,
            interval_between_lessons=Booking.IntervalBetweenLessons.ONE_WEEK,
            day_of_the_week=Booking.DayOfWeek.TUESDAY,
            further_information="Extra Information"
        )
        booking1.save()
        """

        """
        request1 = Request.objects.create(
            user=User.objects.get(
                email='email12@email.com'
            ),
            date=timezone.datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
            number_of_lessons=1,
            interval_between_lessons=Request.IntervalBetweenLessons.ONE_WEEK,
            duration_of_lessons=Request.LessonDuration.THIRTY_MINUTES,
            further_information='Some information...'
        )
        """
        requests = Request.objects.all()
        bookings = Booking.objects.all()
        #for request in requests:
            #for duration in request.LessonDuration.choices:
                #if duration[0] == request.duration_of_lessons:
                    #pass
                    #request.duration_of_lessons = duration[1]
        for req in requests:
            req.interval_between_lessons = req.IntervalBetweenLessons.choices[req.interval_between_lessons-1][1]
            for duration in req.LessonDuration.choices:
                if duration[0] == req.duration_of_lessons:
                    req.duration_of_lessons = duration[1]
        for booking in bookings:
            booking.day_of_the_week = booking.DayOfWeek.choices[booking.day_of_the_week-1][1]
            booking.interval_between_lessons = booking.IntervalBetweenLessons.choices[booking.interval_between_lessons-1][1]
            for duration in booking.LessonDuration.choices:
                if duration[0] == booking.duration_of_lessons:
                    booking.duration_of_lessons = duration[1]
        return render(request, 'admin_view_requests.html', {'requests': requests,
                                                            'bookings': bookings})

