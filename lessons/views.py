from django.shortcuts import render, redirect
from .forms import LogInForm, TransactionSubmitForm, NewRequestForm, NewChildForm, SignUpForm, PasswordForm, UserForm,CreateUser, TermViewForm
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
def request_list(request, relation_id=None):
    user_requests = get_request_objects(user=request.user)
    return render(request, 'request_list.html', {'user_requests': user_requests})

@login_required
@allowed_groups(['Student'])
def booking_list(request, relation_id=None):
    user_bookings = get_booking_objects(user=request.user)
    return render(request, 'booking_list.html', {'user_bookings': user_bookings})

@login_required
@allowed_groups(['Student'])
def request_view(request):
    relation_id = get_relation_id_from_request(request)
    request_id = get_request_id_from_request(request)
    
    if is_child(relation_id):
        redirect_page = 'child_request_list'
    else:
        redirect_page = 'request_list'
    
    if request.method == 'POST':
        if request.POST.get('delete', None) and delete_request_object_from_request(request):
            return redirect(redirect_page, relation_id=relation_id)
            
        elif request.POST.get('update', None) and update_request_object_from_request(request): 
            return redirect(redirect_page, relation_id=relation_id)
        
        elif request.POST.get('return', None):
            return redirect(redirect_page, relation_id=relation_id)
    
    full_name = get_full_name_by_relation_id(request.user, relation_id)
    request_fulfilled = get_request_object(request_id).fulfilled
    
    form = get_request_view_form(request_id)
    
    if request_fulfilled:
        form.set_read_only()
    
    return render(request, 'request_view.html', {'request_id':request_id, 'relation_id':relation_id, 
                                                 'full_name':full_name, 'form':form, 'readonly':request_fulfilled})

@login_required
@allowed_groups(['Student'])
def new_request_view(request):
    relation_id = get_relation_id_from_request(request)
    user = request.user
    
    if request.method == 'POST':
        form = NewRequestForm(user=user, relation_id=relation_id, data=request.POST)
        if form.is_valid():
            form.save()
            if is_child(relation_id):
                return redirect('child_request_list', relation_id=relation_id)
            else:
                return redirect('request_list')
                
        
    full_name = get_full_name_by_relation_id(user, relation_id)
    form = NewRequestForm()
    
    return render(request, 'new_request_view.html', {'relation_id':relation_id, 'full_name':full_name, 'form':form})


@login_required
@allowed_groups(['Student'])
def children_list(request):
    children = get_children_idname(request.user)
    return render(request, 'children_list.html', {'children': children})

@login_required
@allowed_groups(['Student'])
def child_page(request):
    relation_id = get_relation_id_from_request(request)
    
    if request.method == 'GET':
        if request.GET.get('requests', None):
            return redirect('child_request_list', relation_id=relation_id)
        if request.GET.get('bookings', None):
            return redirect('child_booking_list', relation_id=relation_id)
        if request.GET.get('return', None):
            return redirect('children_list')
    
    child = get_child_idname(relation_id)
    
    return render(request, 'child_page.html', {'child':child})

def new_child_view(request):
    if request.method == 'POST':
        form = NewChildForm(user=request.user, data=request.POST)
        form.save()
        return redirect('children_list')
    
    form = NewChildForm()
        
    return render(request, 'new_child_view.html', {'form': form})

@login_required
@allowed_groups(['Student'])
def child_request_list(request, relation_id=None):
    if not relation_id:
        relation_id = get_relation_id_from_request(request)
    
    child = get_child_idname(relation_id)
    child_requests = get_request_objects(request.user, relation_id)
    
    return render(request, 'child_request_list.html', {'child':child, 'child_requests': child_requests})
    

@login_required
@allowed_groups(['Student'])
def child_booking_list(request, relation_id=None):
    if not relation_id:
        relation_id = get_relation_id_from_request(request)
    
    child = get_child_idname(relation_id)
    child_bookings = get_booking_objects(request.user, relation_id)
    
    return render(request, 'child_booking_list.html', {'child':child, 'child_bookings': child_bookings})
    

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
def profile(request,user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = UserForm(instance=user, data=request.POST)
        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "Profile updated!")
            form.save()
            return redirect(get_redirect_url_for_user(user))
    else:
        form = UserForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'user_id':user_id})


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
def admin_bookings_view(request):
    bookings = Booking.objects.all()

    for booking in bookings:
        booking.interval_between_lessons = \
            booking.IntervalBetweenLessons.choices[booking.interval_between_lessons - 1][1]
        for duration in booking.LessonDuration.choices:
            if duration[0] == booking.duration_of_lessons:
                booking.duration_of_lessons = duration[1]
    return render(request, 'admin_bookings_view.html', {'bookings': bookings})

def admin_requests_view(request):
    requests = Request.objects.all()
    fulfilled_requests = []
    unfulfilled_requests = []
    for req in requests:
        req.interval_between_lessons = req.IntervalBetweenLessons.choices[req.interval_between_lessons - 1][1]
        for duration in req.LessonDuration.choices:
            if duration[0] == req.duration_of_lessons:
                req.duration_of_lessons = duration[1]
        req.raw_date = str(req.date).split('+')[0] # To do: Ensure this works regardless of timezone, change
        if req.fulfilled:
            fulfilled_requests.append(req)
        else:
            unfulfilled_requests.append(req)
    return render(request, 'admin_requests_view.html', {'fulfilled_requests': fulfilled_requests,
                                                        'unfulfilled_requests': unfulfilled_requests})


#@login_required
#@allowed_groups(["Admin","Director"])
def fulfil_request_view(request):

    if request.method == 'POST':
        if request.POST.get('fulfil', None):
            form = FulfilRequestForm(request.POST)
            booking_req = form.save()

            if not booking_req[1].fulfilled:
                invoice_number = create_invoice(booking_req[0], booking_req[2])
                booking_req[0].invoice_id = invoice_number
                booking_req[0].full_clean()
                booking_req[1].fulfilled = True
                booking_req[1].save()
                booking_req[0].save()
                return redirect('admin_bookings_view')
            else:
                print('Booking is already fulfilled')
                return redirect('admin_bookings_view')
        elif request.POST.get('delete', None):
            delete_request_object_from_request(request)
            return redirect('admin_requests_view')
        elif request.POST.get('return', None):
            return redirect('admin_requests_view')

    date = str(get_request_object_from_request(request).date)
    form = get_fulfil_request_form(request)
    return render(request, 'fulfil_view.html', {'date': date, 'form': form})


def edit_booking_view(request):
    if request.method == 'POST':
        if request.POST.get('update', None):
            update_booking(request)
        elif request.POST.get('delete', None):
            delete_booking(request)
        return redirect('admin_bookings_view')
    booking = Booking.objects.get(invoice_id=request.GET['inv_id'])
    form = get_booking_form(request)
    return render(request, 'edit_booking.html', {'form': form})

"""
A view that presents a list of all terms.
"""
@login_required
@allowed_groups(["Student"]) # Do Admins also need access to this page?
def student_term_view(request):
    terms = SchoolTerm.objects.all()
    return render(request, 'student_term_view.html', {'terms': terms})

"""
A view to see and edit all terms as well as create a new term.
"""
@login_required
@allowed_groups(["Admin"])
def admin_term_view(request):
    terms = SchoolTerm.objects.all()
    return render(request, 'admin_term_view.html', {'terms': terms})

"""
A view that handles a single term.
"""
@login_required
@allowed_groups(["Admin"])
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

"""
This view enables the creation of a new term.
"""
@login_required
@allowed_groups(["Admin"])
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


"""
This view confirms the deletion of a term.
"""
@login_required
@allowed_groups(["Admin"])
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
        if request.POST.get('edit', None):
            id_user_to_edit = request.POST.get("edit","")
            return redirect("profile",user_id=id_user_to_edit)
        elif request.POST.get('delete', None):
            id_user_to_delete = request.POST.get("delete","")
            user_to_delete = User.objects.get(id=id_user_to_delete)
            user_to_delete.delete()
        elif request.POST.get('promote_director', None):
            id_user_to_promote = request.POST.get("promote_director","")
            user_to_promote = User.objects.get(id=id_user_to_promote)
            if user_to_promote.groups.exists():
                user_to_promote.groups.clear()
            user_to_promote.is_superuser = True
            user_to_promote.is_staff = True
            user_to_promote.save()
        elif request.POST.get('create_director', None):
            return redirect("create_director_user")
        elif request.POST.get('create_student', None):
            return redirect("create_student_user")
        elif request.POST.get('create_administrator', None):
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

