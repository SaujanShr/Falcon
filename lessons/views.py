from django.shortcuts import render, redirect
from .forms import LogInForm, TransactionSubmitForm, NewRequestViewForm, SignUpForm, PasswordForm, UserForm
from .models import Student, Booking, BankTransaction
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .decorators import login_prohibited, allowed_groups
from .views_functions import *
from django.contrib.auth.hashers import check_password


@login_required
@allowed_groups(['Student'])
def student_page(request):
    return render(request, 'student_page.html')


@login_required
@allowed_groups(['Student'])
def request_list(request):
    if request.method == 'POST':
        if 'delete' in request.POST:
            delete_request(request)
        elif 'update' in request.POST:
            update_request(request)

    date_user_request_pairs = get_date_user_request_pairs(request)
    return render(request, 'request_list.html', {'date_user_request_pairs': date_user_request_pairs})




@login_required
@allowed_groups(['Student'])
def request_view(request):
    user_request = get_request_object(request)
    date = str(user_request.date)
    form = get_request_view_form(request)
    request_fulfilled = user_request.fulfilled
    if request_fulfilled:
        form.setReadOnly()
    return render(request, 'request_view.html', {'date': date, 'form': form, 'readonly': request_fulfilled})


@login_required
@allowed_groups(['Student'])
def new_request_view(request):
    if request.method == 'POST':
        form = NewRequestViewForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return redirect('student_page')
    else:
        form = NewRequestViewForm()
    return render(request, 'new_request_view.html', {'form': form})


@login_prohibited
def home(request):
    return render(request, 'home.html')


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            user = get_user(form)
            if user is not None:
                login(request, user)
                redirect_url = get_redirect_url(user, request)
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
    form = LogInForm()
    next_url = request.GET.get('next') or ''
    return render(request, 'log_in.html', {'form': form, 'next': next_url})


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('log_in')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_required
def profile(request):
    current_user = request.user
    if request.method == 'POST':
        form = UserForm(instance=current_user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect('student_page')
    else:
        form = UserForm(instance=current_user)
    return render(request, 'profile.html', {'form': form})


@login_required
def password(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            current_password_input = form.cleaned_data.get('password')
            if check_password(current_password_input, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user)
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('student_page')
            else:
                messages.add_message(request, messages.ERROR, "Current Password is incorrect!")

        # Show error on not matching new password and confirmation
        new_password = form.cleaned_data.get('new_password')
        password_confirmation = form.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            messages.add_message(request, messages.ERROR, "New password and confirmation do not match!")
            return render(request, 'password_change.html', {'form': form})

        messages.add_message(request, messages.ERROR, "New password must contain an uppercase character, a lowercase character and a number")

    form = PasswordForm()
    return render(request, 'password_change.html', {'form': form})


@login_required()
def log_out(request):
    logout(request)
    return redirect('home')


# THIS VIEW IS FOR TESTING PURPOSES, TO DELETE FOR LATER VERSIONS
@login_required
@allowed_groups(["Admin", "Director"])
def test_redirect_view(request):
    return render(request, 'test_redirect.html')


@login_required
@allowed_groups(["Admin", "Director"])
def transaction_admin_view(request):
    if request.method == 'POST':
        form = TransactionSubmitForm(request.POST)
        if form.is_valid():
            form.save()
            form = TransactionSubmitForm()
    else:
        form = TransactionSubmitForm()

    return render(request, 'transaction_admin_view.html', {'form': form})


@login_required
@allowed_groups(["Admin", "Director"])
def transaction_list_admin(request):
    transactions = BankTransaction.objects.order_by('date')
    return render(request, 'transaction_list.html', {'transactions': transactions})


@login_required
@allowed_groups(["Student"])
def transaction_list_student(request):
    # currently errors if user is not logged in
    r_user = request.user
    r_student = Student.objects.get(user=r_user)

    if (not r_student):
        transactions = BankTransaction.objects.none()
    else:
        transactions = BankTransaction.objects.order_by('date').filter(student=r_student)

    return render(request, 'transaction_list.html', {'transactions': transactions})


@login_required
@allowed_groups(["Admin", "Director"])
def balance_list_admin(request):
    students = Student.objects.all()
    return render(request, 'balance_list.html', {'students': students})


#@login_required
#@allowed_groups(["Admin","Director"])
def admin_bookings_requests_view(request):
    requests = Request.objects.all()
    bookings = Booking.objects.all()
    for req in requests:
        req.interval_between_lessons = req.IntervalBetweenLessons.choices[req.interval_between_lessons - 1][1]
        for duration in req.LessonDuration.choices:
            if duration[0] == req.duration_of_lessons:
                req.duration_of_lessons = duration[1]
        req.raw_date = str(req.date).split('+')[0] # To do: Ensure this works regardless of timezone, change
        # implementation if necessary
    for booking in bookings:
        #booking.day_of_the_week = booking.DayOfWeek.choices[booking.day_of_the_week - 1][1]
        booking.interval_between_lessons = \
            booking.IntervalBetweenLessons.choices[booking.interval_between_lessons - 1][1]
        for duration in booking.LessonDuration.choices:
            if duration[0] == booking.duration_of_lessons:
                booking.duration_of_lessons = duration[1]
    return render(request, 'admin_view_requests.html', {'requests': requests,
                                                        'bookings': bookings})


#@login_required
#@allowed_groups(["Admin","Director"])
def fulfil_request_view(request):

    if request.method == 'POST':
        if 'fulfil' in request.POST:
            form = FulfilRequestForm(request.POST)
            booking_req = form.save()

            if not booking_req[1].fulfilled:
                invoice_number = create_invoice(booking_req[0], booking_req[2])
                booking_req[0].invoice_id = invoice_number
                booking_req[0].full_clean()
                booking_req[1].fulfilled = True
                booking_req[1].save()
                booking_req[0].save()
                return redirect('admin_request_view')
            else:
                print('Booking is already fulfilled')

    date = str(get_request_object(request).date)
    form = get_fulfil_request_form(request)
    return render(request, 'fulfil_view.html', {'date': date, 'form': form})

def edit_booking_view(request):
    if request.method == 'POST':
        if 'update' in request.POST:
            update_booking(request)
        elif 'delete' in request.POST:
            delete_booking(request)
        return redirect('admin_request_view')
    booking = Booking.objects.get(invoice_id=request.GET['inv_id'])
    form = get_booking_form(request)
    return render(request, 'edit_booking.html', {'form': form})

