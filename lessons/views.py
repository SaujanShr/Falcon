from django.shortcuts import render
from .forms import LogInForm, NewRequestForm, NewChildForm, SignUpForm, PasswordForm, UserForm, CreateUser, TermEditForm
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
    user_requests = get_and_format_requests_for_display(request.user)
    bookings = get_and_format_bookings_for_display(request.user)
    invoices = get_invoice_list(request)
    transactions = get_transaction_list(request)
    balance = get_student_balance(request)
    return render(request, 'student_page.html', {'user_requests': user_requests[:5],
                                                 'invoices': invoices[:5],
                                                 'transactions': transactions[:5],
                                                 'bookings': bookings[:5],
                                                 'balance': balance})


@login_required
@allowed_groups(['Admin', 'Director'])
def admin_page(request):
    transactions = BankTransaction.objects.order_by('-date')
    requests = get_and_format_requests_for_admin_display()
    bookings = get_and_format_bookings_for_admin_display()
    terms = SchoolTerm.objects.all()
    return render(request, 'admin_page.html', {'transactions': transactions[:5],
                                               'requests': requests['unfulfilled'][:5],
                                               'bookings': bookings[:5], 'terms': terms[:5]})


@login_required
@allowed_groups(['Student'])
def request_list(request):
    user_requests = get_and_format_requests_for_display(request.user)
    balance = get_student_balance(request)
    return render(request, 'request_list.html', {'user_requests': user_requests, 'is_student': True, 'balance': balance})


@login_required
@allowed_groups(['Student'])
def booking_list(request):
    balance = get_student_balance(request)
    user_bookings = get_and_format_bookings_for_display(request.user)
    return render(request, 'booking_list.html', {'user_bookings': user_bookings, 'is_student': True, 'balance': balance})


@login_required
@allowed_groups(['Student', 'Admin', 'Director'])
def request_view(request):
    user = request.user
    request_id = get_request_id_from_request(request)

    user_request = get_request_object(request_id)

    # If the user is not authorised, kick them back to the student page.
    if user != user_request.user and not user.is_admin_or_director():
        return redirect(get_redirect_url_for_user(user))

    relation_id = user_request.relation_id

    if request.method == 'POST':
        if request.POST.get('delete', None) and delete_request_object_from_request(request):
            return redirect_to_request_list(user, relation_id)

        elif request.POST.get('update', None) and update_request_object_from_request(request):
            return redirect_to_request_list(user, relation_id)

        elif request.POST.get('return', None):
            return redirect_to_request_list(user, relation_id)

    full_name = get_full_name_by_relation_id(user_request.user, relation_id)
    readonly = user.is_admin_or_director() or user_request.fulfilled

    form = get_request_view_form(request_id)
    if not form:
        return redirect_to_request_list(user, relation_id)

    if readonly:
        form.set_read_only()

    balance = get_student_balance(request)
    return render(request, 'request_view.html', {'request_id': request_id, 'relation_id': relation_id,
                                                 'full_name': full_name, 'form': form, 'readonly': readonly, 'balance': balance})


@login_required
@allowed_groups(['Student', 'Admin', 'Director'])
def invoice_view(request):
    user = request.user

    # Only possible post request is the 'Return' button/
    if request.method == 'POST':
        return redirect_to_invoice_list(user)

    invoice_id = get_invoice_id_from_request(request)
    form = get_invoice_view_form(invoice_id)

    if not form:
        return redirect_to_invoice_list(user)

    if not user_authorised_to_see_invoice(request, invoice_id): return redirect_to_invoice_list(user)
    balance = get_student_balance(request)
    return render(request, 'invoice_view.html', {'form': form, 'invoice_id': invoice_id, 'balance': balance})


@login_required
@allowed_groups(['Student'])
def new_request_view(request):
    relation_id = get_relation_id_from_request(request)
    user = request.user

    if request.method == 'POST':
        form = NewRequestForm(user=user, relation_id=relation_id, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect_to_request_list(user, relation_id)

    full_name = get_full_name_by_relation_id(user, relation_id)
    form = NewRequestForm()

    balance = get_student_balance(request)
    return render(request, 'new_request_view.html', {'relation_id': relation_id, 'full_name': full_name, 'form': form, 'balance': balance})


@login_required
@allowed_groups(['Student'])
def children_list(request):
    children = get_children_idname(request.user)
    balance = get_student_balance(request)
    return render(request, 'children_list.html', {'children': children, 'balance':balance})


@login_required
@allowed_groups(['Student'])
def child_page(request):
    relation_id = get_relation_id_from_request(request)

    if not child_exists(relation_id) or not user_is_parent(request, relation_id):
        return redirect('children_list')

    if request.method == 'GET':
        if request.GET.get('requests', None):
            return redirect_with_queries('child_request_list', relation_id=relation_id)

        if request.GET.get('bookings', None):
            return redirect_with_queries('child_booking_list', relation_id=relation_id)

        if request.GET.get('lessons', None):
            return redirect_with_queries('lesson_list_child', relation_id=relation_id)

        if request.GET.get('return', None):
            return redirect('children_list')

    child = get_child_idname(relation_id)
    user_requests = get_and_format_requests_for_display(request.user, relation_id)
    bookings = get_and_format_bookings_for_display(request.user, relation_id)
    balance = get_student_balance(request)
    return render(request, 'child_page.html', {
        'child': child,
        'user_requests': user_requests[:5],
        'bookings': bookings[:5],
        'balance': balance
    })


@login_required
@allowed_groups(['Student'])
def new_child_view(request):
    if request.method == 'POST':
        form = NewChildForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('children_list')

    form = NewChildForm()
    balance = get_student_balance(request)
    return render(request, 'new_child_view.html', {'form': form, 'balance': balance})


@login_required
@allowed_groups(['Student'])
def child_view(request):
    relation_id = get_relation_id_from_request(request)

    if not child_exists(relation_id) or not user_is_parent(request, relation_id):
        return redirect('children_list')

    if request.method == 'POST':
        if request.POST.get('update', None) and update_child_object_from_request(request):
            return redirect('children_list')

        if request.POST.get('delete', None):
            delete_child(request.user, request.POST.get('relation_id'))
            return redirect('children_list')

        elif request.POST.get('return', None):
            return redirect('children_list')

    form = get_child_view_form(relation_id)

    if not form:
        return redirect('children_list')

    balance = get_student_balance(request)
    return render(request, 'child_view.html', {'relation_id': relation_id, 'form': form, 'balance': balance})


@login_required
@allowed_groups(['Student'])
def child_request_list(request):
    relation_id = get_relation_id_from_request(request)

    if not child_exists(relation_id) or not user_is_parent(request, relation_id):
        return redirect('children_list')

    child = get_child_idname(relation_id)
    child_requests = get_and_format_requests_for_display(request.user, relation_id)

    balance = get_student_balance(request)
    return render(request, 'child_request_list.html', {'child': child, 'child_requests': child_requests, 'balance': balance})


@login_required
@allowed_groups(['Student'])
def child_booking_list(request):
    relation_id = get_relation_id_from_request(request)

    if not child_exists(relation_id) or not user_is_parent(request, relation_id):
        return redirect('children_list')

    child = get_child_idname(relation_id)
    child_bookings = get_booking_objects(request.user, relation_id)

    balance = get_student_balance(request)
    return render(request, 'child_booking_list.html', {'child': child, 'child_bookings': child_bookings, 'balance':balance})


@login_required
@allowed_groups(['Admin', 'Director'])
def lesson_list_admin(request):
    bookings = Booking.objects.all()
    lessons = generate_lessons_from_bookings(bookings)
    lesson_falls_in_holiday = check_if_lessons_not_in_termtime(lessons)
    return render(request, 'lesson_list.html', {'lessons': lessons, 'lesson_falls_in_holiday': lesson_falls_in_holiday})


@login_required
@allowed_groups(['Student'])
def lesson_list_student(request):
    relation_id = get_relation_id_from_request(request)
    bookings = get_booking_objects(request.user, relation_id)

    lessons = generate_lessons_from_bookings(bookings)
    lesson_falls_in_holiday = check_if_lessons_not_in_termtime(lessons)
    balance = get_student_balance(request)
    return render(request, 'lesson_list.html', {'lessons': lessons, 'lesson_falls_in_holiday': lesson_falls_in_holiday, 'balance': balance})


@login_required
@allowed_groups(['Student'])
def lesson_list_child(request):
    relation_id = get_relation_id_from_request(request)

    if not child_exists(relation_id) or not user_is_parent(request, relation_id):
        return redirect('children_list')

    child = get_child_idname(relation_id)
    child_bookings = get_booking_objects(request.user, relation_id)

    lessons = generate_lessons_from_bookings(child_bookings)
    lesson_falls_in_holiday = check_if_lessons_not_in_termtime(lessons)

    balance = get_student_balance(request)
    return render(request, 'child_lesson_list.html',
                  {'lessons': lessons, 'child': child, 'lesson_falls_in_holiday': lesson_falls_in_holiday, 'balance': balance})


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
                redirect_url = request.POST.get('next') or get_redirect_url_for_user(user)
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
    # Redirect if the requested user_id is not a valid user.
    user_id = request.GET.get('user_id', None)
    if not user_id:
        return redirect_with_queries('/profile/', user_id=request.user.id)

    # Check if there exists a user with user_id
    if len(User.objects.filter(id=user_id)) == 0:
        return redirect_with_queries('/profile/', user_id=request.user.id)

    user = User.objects.get(id=user_id)

    # Redirect if the current user is attempting to change the profile of another user.
    if not request.user.is_superuser and request.user != user:
        return redirect_with_queries('/profile/', user_id=request.user.id)

    if request.method == 'POST':
        form = UserForm(instance=user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect(get_redirect_url_for_user(user))
    else:
        form = UserForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'user_id': user.id})


@login_required
def change_user_password(request):
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
                return redirect(get_redirect_url_for_user(current_user))
            else:
                messages.add_message(request, messages.ERROR, "Current Password is incorrect!")

        # Show error on not matching new password and confirmation
        new_password = form.cleaned_data.get('new_password')
        password_confirmation = form.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            messages.add_message(request, messages.ERROR, "New password and confirmation do not match!")
            return render(request, 'password_change.html', {'form': form})

        messages.add_message(request, messages.ERROR,
                             "New password must contain an uppercase character, a lowercase character and a number")

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
    transactions = BankTransaction.objects.order_by('-date')
    return render(request, 'transaction_list.html', {'transactions': transactions})


@login_required
@allowed_groups(["Student"])
def transaction_list_student(request):
    transactions = get_transaction_list(request)
    balance = get_student_balance(request)
    return render(request, 'transaction_list.html', {'transactions': transactions, 'balance': balance})


@login_required
@allowed_groups(["Admin", "Director"])
def invoice_list_admin(request):
    invoices = Invoice.objects.all().order_by('-invoice_number')
    return render(request, 'invoice_list.html', {'invoices': invoices})


@login_required
@allowed_groups(["Student"])
def invoice_list_student(request):
    invoices = get_invoice_list(request)
    balance = get_student_balance(request)
    return render(request, 'invoice_list.html', {'invoices': invoices, 'balance':balance})


@login_required
@allowed_groups(["Admin", "Director"])
def balance_list_admin(request):
    students = Student.objects.all()
    return render(request, 'balance_list.html', {'students': students})


@login_required
@allowed_groups(["Admin", "Director"])
def admin_booking_list(request):
    bookings = get_and_format_bookings_for_admin_display()
    return render(request, 'admin_booking_list.html', {'bookings': bookings})


@login_required
@allowed_groups(["Admin", "Director"])
def admin_request_list(request):
    requests = get_and_format_requests_for_admin_display()

    return render(request, 'admin_request_list.html', {'fulfilled_requests': requests['fulfilled'],
                                                       'unfulfilled_requests': requests['unfulfilled']})


@login_required
@allowed_groups(["Admin","Director"])
def fulfil_request_view(request):
    request_id = get_request_id_from_request(request)

    if request.method == 'POST':
        if request.POST.get('fulfil', None):
            form = FulfilRequestForm(request_id=request_id, data=request.POST)
            if form.is_valid():
                booking = form.save()
            return redirect('admin_booking_list')
        elif request.POST.get('delete', None):
            delete_request_object_from_request(request)
            return redirect('admin_request_list')
        elif request.POST.get('return', None):
            return redirect('admin_request_list')
    form = get_fulfil_request_form(request)
    return render(request, 'fulfil_view.html', {'request_id': request_id, 'form': form})


def booking_view(request):
    booking_id = get_booking_id_from_request(request)
    booking = get_booking_object(booking_id)
    user = request.user

    # If the user is not authorised, kick them back to the student page.
    if user != booking.user and not user.is_admin_or_director():
        return redirect('student_page')

    relation_id = booking.relation_id

    if user.is_admin_or_director():
        redirect_page = 'admin_booking_list'
    elif is_child(relation_id):
        redirect_page = 'child_booking_list'
    else:
        redirect_page = 'booking_list'

    if request.method == 'POST':
        if request.POST.get('delete', None) and delete_booking(request):
            return redirect_with_queries(redirect_page, relation_id=relation_id)

        elif request.POST.get('update', None) and update_booking(request):
            return redirect_with_queries(redirect_page, relation_id=relation_id)

        elif request.POST.get('return', None):
            return redirect_with_queries(redirect_page, relation_id=relation_id)

    full_name = get_full_name_by_relation_id(booking.user, relation_id)
    readonly = not user.is_admin_or_director()

    form = get_booking_form(booking_id)

    if readonly:
        form.set_read_only()

    balance = get_student_balance(request)
    return render(request, 'booking_view.html', {'booking_id': booking_id, 'relation_id': relation_id,
                                                 'full_name': full_name, 'form': form, 'readonly': readonly, 'balance':balance})


@login_required
@allowed_groups(["Student"])
def student_term_view(request):
    terms = SchoolTerm.objects.all()
    balance = get_student_balance(request)
    return render(request, 'student_term_view.html', {'terms': terms, 'balance':balance})



@login_required
@allowed_groups(["Admin", "Director"])
def admin_term_view(request):
    terms = SchoolTerm.objects.all()
    return render(request, 'admin_term_view.html', {'terms': terms})


@login_required
@allowed_groups(["Admin", "Director"])
def term_view(request):
    # Check that the get request includes a value for term_id
    if request.method == 'GET' and request.GET['term_id'] != '':
        term_id = request.GET['term_id']
        # Check to see if the term id in the get request exists.
        if SchoolTerm.objects.filter(id=term_id).exists():
            term = SchoolTerm.objects.get(id=request.GET['term_id'])
            form = TermEditForm(instance=term)
            return render(request, "term_view.html", {'form': form, 'term_id': term.id, 'term_name': term.term_name})

    if request.method == 'POST':
        term_id = request.POST['term_id']
        # Check to see if the term_id exists then get the term object, otherwise redirect.
        if SchoolTerm.objects.filter(id=request.POST['term_id']).exists():
            term = SchoolTerm.objects.get(id=term_id)
        else:
            return redirect('admin_term_view')

        # Create a copy of the request data, and delete term, Otherwise term name validation (Unique constraint)
        data = request.POST.copy()
        term.delete()
        form = TermEditForm(data)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Term updated!")
        else:
            SchoolTerm(term_name=term.term_name, start_date=term.start_date, end_date=term.end_date).save()
            new_term = SchoolTerm.objects.get(term_name=term.term_name)
            return render(request, 'term_view.html', {'form': form, 'term_id': new_term.id, 'term_name': term.term_name})

    return redirect('admin_term_view')

@login_required
@allowed_groups(["Admin", "Director"])
def new_term_view(request):
    if request.method == 'POST':
        form = TermEditForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Term created!")
            return redirect('admin_term_view')
    else:
        form = TermEditForm()
    return render(request, 'new_term_view.html', {'form': form})


@login_required
@allowed_groups(["Admin", "Director"])
def term_deletion_confirmation_view(request):
    if request.method == 'GET' and request.GET.__contains__('term_name'):
        term_name = request.GET['term_name']
        return render(request, 'term_deletion_confirmation.html', {'term_name': term_name})
    if request.method == 'POST':
        if SchoolTerm.objects.filter(term_name=request.POST['term_name']).exists():
            term = SchoolTerm.objects.get(term_name=request.POST['term_name'])
            term.delete()
            messages.add_message(request, messages.SUCCESS, "Term deleted!")
        else:
            messages.add_message(request, messages.ERROR, "Term does not exist!")

    return redirect(admin_term_view)


@login_required
@allowed_groups(["Director"])
def admin_user_list(request):
    if request.method == 'POST':
        if request.POST.get('edit', None):
            id_user_to_edit = request.POST.get("edit", "")
            return redirect_with_queries("profile", user_id=id_user_to_edit)
        elif request.POST.get('delete', None):
            id_user_to_delete = request.POST.get("delete", "")
            user_to_delete = User.objects.get(id=id_user_to_delete)
            user_to_delete.delete()
        elif request.POST.get('promote_director', None):
            id_user_to_promote = request.POST.get("promote_director", "")
            user_to_promote = User.objects.get(id=id_user_to_promote)
            if user_to_promote.groups.exists():
                user_to_promote.groups.clear()
            user_to_promote.is_superuser = True
            user_to_promote.is_staff = True
            user_to_promote.save()
        elif request.POST.get('create_director') == '':
            return redirect("create_director_user")
        elif request.POST.get('create_administrator') == '':
            return redirect("create_admin_user")

    users = User.objects.order_by("groups")
    user_to_display = []
    for user in users:
        if user.is_admin_or_director():
            user_to_display.append(user)
    return render(request, 'admin_user_list.html', {'users': user_to_display})

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
            return redirect('admin_user_list')
    else:
        form = CreateUser()
    return render(request, 'create_user.html', {'form': form, 'user_type': "Director"})


@login_required
@allowed_groups("Director")
def create_admin_user(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            created_user = form.save()
            admin_group = Group.objects.get(name='Admin')
            admin_group.user_set.add(created_user)
            return redirect('admin_user_list')
    else:
        form = CreateUser()
    return render(request, 'create_user.html', {'form': form, 'user_type': "Administrator"})
