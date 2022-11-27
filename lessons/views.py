from django.shortcuts import render, redirect
from .forms import LogInForm, TransactionSubmitForm, NewRequestViewForm, SignUpForm, PasswordForm, UserForm,CreateUser, TermViewForm
from .models import Student, Booking, BankTransaction, User
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .decorators import login_prohibited, allowed_groups
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from .views_functions import *

@login_required
@allowed_groups(['Student'])
def student_page(request):
    return render(request, 'student_page.html')

@login_required
@allowed_groups(['Admin', 'Director'])
def admin_page(request):
    transactions = BankTransaction.objects.order_by('date')
    #TODO add requests and bookings data to pass into template
    #TODO if any of these datasets are too large, filter to only first 15
    return render(request, 'admin_page.html', {'transactions': transactions})


@login_required
@allowed_groups(['Student'])
def request_list(request):
    date_user_request_pairs = get_date_user_request_pairs(request)
    return render(request, 'request_list.html', {'date_user_request_pairs': date_user_request_pairs})


@login_required
@allowed_groups(['Student'])
def request_view(request):
    if request.method == 'POST':
        if 'delete' in request.POST: 
            if delete_request(request):
                return redirect('request_list')
        elif 'update' in request.POST: 
            if update_request(request):
                return redirect('request_list')
    
    user_request = get_request_object(request)
    date = str(user_request.date)
    form = get_new_request_view_form(request)
    
    request_fulfilled = user_request.fulfilled
    if request_fulfilled: form.set_read_only()
    
    return render(request, 'request_view.html', {'date': date, 'form': form, 'readonly': request_fulfilled})


@login_required
@allowed_groups(['Student'])
def new_request_view(request):
    if request.method == 'POST':
        if save_new_request(request):
            return redirect('request_list')
    
    form = NewRequestViewForm(request.user)
    return render(request, 'new_request_view.html', {'form': form})


@login_required
@allowed_groups(['Student'])
def children_list(request):
    children = get_children(request)
    return render(request, 'children_list.html', {'children': children})

@login_required
@allowed_groups(['Student'])
def child_page(request):
    child = get_child(request)
    return render(request, 'child_page.html', {'child': child})

@login_required
@allowed_groups(['Student'])
def child_request_list(request):
    child = get_child(request)

@login_required
@allowed_groups(['Student'])
def child_booking_list(request):
    pass

@login_required
@allowed_groups(['Student'])   

@login_required
@allowed_groups(['Student'])
def booking_list(request):
    return render(request, 'booking_list.html')

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
def profile(request,user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserForm(instance=user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            if user.groups.all()[0].name == "Student":
                return redirect('student_page')
            elif user.groups.all()[0].name == "Admin":
                return redirect('admin_page')
    else:
        form = UserForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'user_id':user_id})


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
                if current_user.groups.all()[0].name == "Student":
                    return redirect('student_page')
                elif current_user.groups.all()[0].name == "Admin":
                    return redirect('admin_page')
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


# @login_required
# @allowed_groups(["Admin"])
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
        # for request in requests:
        # for duration in request.LessonDuration.choices:
        # if duration[0] == request.duration_of_lessons:
        # pass
        # request.duration_of_lessons = duration[1]
        for req in requests:
            req.interval_between_lessons = req.IntervalBetweenLessons.choices[req.interval_between_lessons - 1][1]
            for duration in req.LessonDuration.choices:
                if duration[0] == req.duration_of_lessons:
                    req.duration_of_lessons = duration[1]
        for booking in bookings:
            booking.day_of_the_week = booking.DayOfWeek.choices[booking.day_of_the_week - 1][1]
            booking.interval_between_lessons = \
                booking.IntervalBetweenLessons.choices[booking.interval_between_lessons - 1][1]
            for duration in booking.LessonDuration.choices:
                if duration[0] == booking.duration_of_lessons:
                    booking.duration_of_lessons = duration[1]
        return render(request, 'admin_view_requests.html', {'requests': requests,
                                                            'bookings': bookings})

@login_required
@allowed_groups(["Student"]) # Do Admins also need access to this page?
# A view for students to see all terms.
def student_term_view(request):
    terms = SchoolTerm.objects.all()
    return render(request, 'student_term_view.html', {'terms': terms})


@login_required
@allowed_groups(["Admin"])
# A view for admins to see and edit all terms as well access to button to create a new term.
def admin_term_view(request):
    terms = SchoolTerm.objects.all()
    return render(request, 'admin_term_view.html', {'terms': terms})


@login_required
@allowed_groups(["Admin"])
# A view for a single term
def term_view(request):
    # Check whether the get request contains term_name, otherwise redirect back to term view.
    if request.method == 'GET' and request.GET.__contains__('term_name'):
        term = SchoolTerm.objects.get(term_name=request.GET['term_name'])
        form = TermViewForm(instance=term)
        # Use old_term_name, so we can get the term object in case the user changes the term name.
        old_term_name = request.GET['term_name']
        return render(request, "term_view.html", {'form': form, 'old_term_name': old_term_name})

    if request.method == 'POST':
        # Use old term name in case the user has changed the term name.
        term = SchoolTerm.objects.get(term_name=request.POST['old_term_name'])
        old_term_name = request.POST['old_term_name']
        new_term_name = request.POST['term_name']
        old_start_date = term.start_date
        old_end_date = term.end_date

        initial_form = TermViewForm(instance=term)

        # Check if there already exists a term with the same name, if there is a change in the name of the term.
        if term_name_already_exists(old_term_name, new_term_name):
            messages.add_message(request, messages.ERROR, "There already exists a term with this name!")
            return render(request, "term_view.html", {'form': initial_form, 'old_term_name': old_term_name})

        # Create a copy of the request data, and delete term, Otherwise term name validation (Unique constraint)
        data = request.POST.copy()
        term.delete()
        form = TermViewForm(data)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Term updated!")
        else:
            # If any other fields are invalid then recreate old term again, very bad!
            SchoolTerm(term_name=old_term_name, start_date=old_start_date, end_date=old_end_date).save()
            return render(request, 'term_view.html', {'form': form, 'old_term_name': old_term_name})

    return redirect('admin_term_view')


@login_required
@allowed_groups(["Admin"])
# A view for creating a new term
def new_term_view(request):
    if request.method == 'POST':
        form = TermViewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Term created!")
            return redirect('admin_term_view')
    else:
        form = TermViewForm()
    return render(request, 'new_term_view.html', {'form': form})


@login_required
@allowed_groups(["Admin"])
# A view to confirm term deletion.
def term_deletion_confirmation_view(request):
    if request.method == 'GET' and request.GET.__contains__('old_term_name'):
        old_term_name = request.GET['old_term_name']
        return render(request, 'term_deletion_confirmation.html', {'old_term_name': old_term_name})
    if request.method == 'POST':
        term = SchoolTerm.objects.get(term_name=request.POST['old_term_name'])
        term.delete()

    return redirect(admin_term_view)

@login_required
@allowed_groups(["Director"])
def admin_user_list_view(request):
    if request.method == 'POST':
        if 'edit' in request.POST: 
            id_user_to_edit = request.POST.get("edit","")
            return redirect("profile",user_id=id_user_to_edit)
        elif 'delete' in request.POST:
            id_user_to_delete = request.POST.get("delete","")
            user_to_delete = User.objects.get(id=id_user_to_delete)
            user_to_delete.delete()
        elif 'promote_director' in request.POST:
            id_user_to_promote = request.POST.get("promote_director","")
            user_to_promote = User.objects.get(id=id_user_to_promote)
            if user_to_promote.groups.exists():
                user_to_promote.groups.clear()
            user_to_promote.is_superuser = True
            user_to_promote.is_staff = True
            user_to_promote.save()
        elif 'create_director' in request.POST:
            return redirect("create_director_user")
        elif 'create_student' in request.POST:
            return redirect("create_student_user")
        elif 'create_administrator' in request.POST:
            return redirect("create_admin_user")

    users = User.objects.all().order_by("groups")
    return render(request,'admin_user_list.html', {'users':users})

@login_required
@allowed_groups("Director")
def create_director_user(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            created_user = form.save()
            created_user.is_superuser = True
            created_user.is_staff = True
            created_user.save()
            return redirect('admin_user_view')
    else:
        form = CreateUser()
    return render(request, 'create_user.html', {'form': form,'user_type':"Director"})

@login_required
@allowed_groups("Director")
def create_admin_user(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            created_user = form.save()
            admin_group = Group.objects.get(name='Admin')
            admin_group.user_set.add(created_user)
            return redirect('admin_user_view')
    else:
        form = CreateUser()
    return render(request, 'create_user.html', {'form': form,'user_type':"Administrator"})

@login_required
@allowed_groups("Director")
def create_student_user(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            created_user = form.save()
            student_group = Group.objects.get(name='Student')
            student_group.user_set.add(created_user)
            return redirect('admin_user_view')
    else:
        form = CreateUser()
    return render(request, 'create_user.html', {'form': form,'user_type':"Student"})

