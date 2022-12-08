import decimal
import urllib
from django.utils import timezone
from .models import User, Request, Invoice, Student, Child, Booking, DayOfTheWeek, SchoolTerm, BankTransaction
from .forms import RequestEditForm, FulfilRequestForm, BookingEditForm, ChildEditForm, TransactionSubmitForm, InvoiceEditForm
from .utils import *
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import redirect
import datetime

def redirect_with_queries(url, **queries):
    '''Redirect with a queryset of given queries'''
    response = redirect(url)
    if queries:
        query_string = urllib.parse.urlencode(queries)
        response['location'] += '?' + query_string
    return response

def get_prev_url_from_request(request):
    '''Get the previous url of a request'''
    if request.method == 'GET':
        return request.GET.get('prev_url', None)
    elif request.method == 'POST':
        return request.POST.get('prev_url', None)
    return None

def get_invoice_id_from_request(request):
    '''Get the unique invoice id parameter from a request'''
    if request.method == 'GET':
        return request.GET.get('invoice_id', None)
    elif request.method == 'POST':
        return request.POST.get('invoice_id', None)
    return None

def get_invoice_object(invoice_id):
    '''Get the invoice with the given id'''
    if Invoice.objects.filter(invoice_number=invoice_id).exists():
        return Invoice.objects.get(invoice_number=invoice_id)
    return None

def get_invoice_object_from_request(request):
    '''Get the invoice with the invoice id parameter from a request'''
    return get_invoice_object(get_invoice_id_from_request(request))

def get_request_object(request_id):
    '''Get the request with the given id'''
    if Request.objects.filter(id=request_id).exists:
        return Request.objects.get(id=request_id)
    return None

def get_booking_object(booking_id):
    '''Get the booking with the given id'''
    if Booking.objects.filter(id=booking_id).exists:
        return Booking.objects.get(id=booking_id)
    return None

def get_child_object(relation_id):
    '''Get the child with the given id'''
    if Child.objects.filter(id=relation_id).exists:
        return Child.objects.get(id=relation_id)
    return None
    
def get_student_balance(request):
    '''Get the balance of the student/parent'''
    if Student.objects.filter(user=request.user).exists():
        student = Student.objects.get(user=request.user)
        return student.balance
    return None

def get_invoice_object(invoice_number):
    '''Get the invoice with the given invoice number'''
    if Invoice.objects.filter(invoice_number=invoice_number).exists():
        return Invoice.objects.get(invoice_number=invoice_number)
    return None

def get_request_id_from_request(request):
    '''Get the unique request id parameter from a request'''
    if request.method == 'GET':
        return request.GET.get('request_id', None)
    elif request.method == 'POST':
        return request.POST.get('request_id', None)
    return None

def get_relation_id_from_request(request):
    '''Get the unique relation id parameter from a request'''
    if request.method == 'GET':
        return request.GET.get('relation_id', -1)
    elif request.method == 'POST':
        return request.POST.get('relation_id', -1)
    return None

def get_booking_id_from_request(request):
    '''Get the unique booking id parameter from a request'''
    if request.method == 'GET':
        return request.GET.get('booking_id', None)
    elif request.method == 'POST':
        return request.POST.get('booking_id', None)
    return None

def get_request_object_from_request(request):
    '''Get the request with the request id parameter from a request'''
    return get_request_object(get_request_id_from_request(request))

def get_child_object_from_request(request):
    '''Get the child with the relation id parameter from a request'''
    return get_child_object(get_relation_id_from_request(request))

def get_booking_object_from_request(request):
    '''Get the booking with the booking id parameter from a request'''
    return get_booking_object(get_booking_id_from_request(request))

def is_child(relation_id):
    '''Validate if a relation id belongs to a child'''
    return int(relation_id) != -1

def get_client_from_relation_id(user, relation_id):
    '''Get the object that matches the given user and relation id'''
    if is_child(relation_id):
        return get_child_object(relation_id=relation_id)
    else:
        return user

def get_request_objects(user, relation_id = -1):
    '''Get a list of requests that match the given user and relation id in a descending date order'''
    return Request.objects.filter(user=user, relation_id=relation_id).order_by('-date')

def delete_request_object_from_request(request):
    '''Delete a request with the request id parameter from a request'''
    return get_request_object_from_request(request).delete()

def update_request_object_from_request(request):
    '''Update a request with the request id parameter from a request'''
    user_request = get_request_object_from_request(request)
    data = request.POST
    
    form = RequestEditForm(instance_id=user_request.id, data=data)
    
    if form.is_valid():
        return form.save()

def get_booking_objects(user, relation_id = -1):
    '''Get a list of bookings that match the given user and relation id in a descending start date order'''
    return Booking.objects.filter(user=user, relation_id=relation_id).order_by('start_date')

def get_full_name(student):
    '''Get the full name of a client (student or child)'''
    if student:
        return f'{student.first_name} {student.last_name}'

def get_full_name_by_relation_id(user, relation_id):
    '''Get the full name of the client with the given user and relation id'''
    get_full_name(get_client_from_relation_id(user, relation_id))

def get_child_idname(relation_id):
    '''Get a child's id and full name pair (idname)'''
    child = get_child_object(relation_id)
    if child:
        return {'id':child.id, 'name':get_full_name(child)}

def get_children(user):
    '''Get the children of a given user'''
    return Child.objects.filter(parent=user)

def get_children_idname(user):
    '''Get a list of the a user's children's idnames'''
    children = get_children(user)
    children_idname = []
    for child in children:
        children_idname.append(get_child_idname(child.id))
    return children_idname

def delete_child(user, relation_id):
    '''Delete a child and their given requests and bookings. Refund bookings if valid'''
    get_request_objects(user, relation_id).delete()
    bookings = get_booking_objects(user, relation_id)
    for booking in bookings:
        refund_booking_if_valid(booking)
    bookings.delete()
        
    return get_child_object(relation_id).delete()

def update_child_object_from_request(request):
    '''Update a child's details with the relation id from a request'''
    child = get_child_object_from_request(request)
    data = request.POST
    
    form = ChildEditForm(instance_id=child.id, data=data)
    if form.is_valid():
        return form.save()

def format_request_for_display(request: Request):
    '''Get a request in a readable format'''
    request.interval_between_lessons = Request.IntervalBetweenLessons.choices[
        Request.IntervalBetweenLessons.values.index(request.interval_between_lessons)
    ][1]
    request.duration_of_lessons = request.LessonDuration.choices[
        request.LessonDuration.values.index(request.duration_of_lessons)
    ][1]
    request.date = request.date.date()
    request.student_name = get_full_name_by_relation_id(request.user, request.relation_id)
    
    return request

def get_and_format_requests_for_display(user, relation_id=-1):
    '''Get the requests that match a given user and relation id in a readable format'''
    requests = get_request_objects(user, relation_id)
    formatted_requests = []
    
    for request in requests:
        formatted_requests.append(format_request_for_display(request))
    
    return formatted_requests

def get_and_format_requests_for_admin_display():
    '''Get a list of all fulfilled requests and a list of all unfulfilled requests in a readable format'''
    requests = Request.objects.all()
    formatted_request_set = {'fulfilled': [], 'unfulfilled': []}
    
    for request in requests:
        request = format_request_for_display(request)
        
        if request.fulfilled:
            formatted_request_set['fulfilled'].append(request)
        else:
            formatted_request_set['unfulfilled'].append(request)
            
    return formatted_request_set

def format_booking_for_display(booking: Booking):
    '''Get a booking in a readable format'''
    booking.interval_between_lessons = Booking.IntervalBetweenLessons.choices[
        Booking.IntervalBetweenLessons.values.index(booking.interval_between_lessons)
    ][1]
    booking.duration_of_lessons = Booking.LessonDuration.choices[
        Booking.LessonDuration.values.index(booking.duration_of_lessons)
    ][1]
    booking.student_name = get_full_name_by_relation_id(booking.user, booking.relation_id)
    
    return booking

def get_and_format_bookings_for_display(user, relation_id=-1):
    '''Get the requests that match a given user and relation id in a readable format'''
    bookings = get_booking_objects(user, relation_id)
    formatted_bookings = []
    
    for booking in bookings:
        formatted_bookings.append(format_booking_for_display(booking))
    
    return formatted_bookings

def get_and_format_bookings_for_admin_display():
    '''Get a list of all bookings in a readable format'''
    bookings = Booking.objects.all()
    formatted_bookings = []

    for booking in bookings:
        formatted_bookings.append(format_booking_for_display(booking))
    
    return formatted_bookings


def refund_booking_if_valid(booking: Booking):
    if booking.start_date <= timezone.now().date():
        return

    invoice = get_invoice_object(booking.invoice_id)
    student = Student.objects.get(user=booking.user)
    paid_amount = invoice.paid_amount
    student.balance += paid_amount
    invoice.paid_amount = 0
    invoice.full_amount = 0
    invoice.fully_paid = True
    invoice.save()
    student.save()

def update_booking(request):
    data = request.POST
    booking_id = get_booking_id_from_request(request)

    form = BookingEditForm(data=data, instance_id=booking_id)
    if not form.is_valid():
        return
    form.save()

    booking = get_booking_object(booking_id)
    
    return booking

def delete_booking(request):
    booking = get_booking_object_from_request(request)
    refund_booking_if_valid(booking)
    return booking.delete()

def get_booking_form(booking_id):
    booking = get_booking_object(booking_id)
    if not booking:
        return
    
    invoice = Invoice.objects.get(invoice_number=booking.invoice_id)
    hourly_cost = float(invoice.full_amount / booking.duration_of_lessons / booking.number_of_lessons * 60)
    form = BookingEditForm(
        initial={
            'invoice': booking.invoice,
            'day_of_the_week': booking.day_of_the_week,
            'time_of_the_day': booking.time_of_the_day,
            'teacher': booking.teacher,
            'start_date': booking.start_date,
            'end_date': booking.end_date,
            'duration_of_lessons': booking.duration_of_lessons,
            'interval_between_lessons': booking.interval_between_lessons,
            'number_of_lessons': booking.number_of_lessons,
            'further_information': booking.further_information,
            'hourly_cost':hourly_cost
        }
    )
    return form

def get_child_view_form(request_id):
    child = get_child_object(request_id)
    if not child:
        return
    
    form = ChildEditForm(
        initial={
            'first_name':child.first_name,
            'last_name':child.last_name
        }
    )
    return form

def get_invoice_view_form(invoice_id):
    invoice = get_invoice_object(invoice_id)
    if not invoice:
        return
    
    form = InvoiceEditForm(
        initial={
            'invoice_number':invoice.invoice_number,
            'student_name': invoice.student.user.email,
            'full_amount': invoice.full_amount,
            'paid_amount': invoice.paid_amount,
        }
    )

    return form


def get_request_view_form(request_id):
    user_request = get_request_object(request_id)
    if not user_request:
        return

    form = RequestEditForm(
        initial={
            'date':user_request.date,
            'relation_id':user_request.relation_id,
            'availability':user_request.availability.all(),
            'number_of_lessons':user_request.number_of_lessons,
            'interval_between_lessons':user_request.interval_between_lessons,
            'duration_of_lessons':user_request.duration_of_lessons,
            'further_information':user_request.further_information,
            'fulfilled':user_request.fulfilled
            }
        )
    return form

def get_upcoming_term(): #Returns the next term
    return SchoolTerm.objects.all().filter(end_date__gt=datetime.date.today()) \
        .filter(start_date__gte=datetime.date.today()).order_by('start_date').first()

#Finds term associated with date, but allows a None return when no term can be associated with the day.
def find_term_from_date_allow_none(date):
    return SchoolTerm.objects.all().filter(end_date__gte=date).filter(start_date__lte=date).first()

def get_fulfil_request_form(request):
    this_request = get_request_object_from_request(request)
    next_term = get_upcoming_term()

    form = FulfilRequestForm(
        initial={
            'start_date': next_term.start_date,
            'end_date': next_term.end_date,
            'number_of_lessons': this_request.number_of_lessons,
            'interval_between_lessons': this_request.interval_between_lessons,
            'duration_of_lessons': this_request.duration_of_lessons,
            'further_information': this_request.further_information
        },
        request_id=this_request.id
    )
    return form

def get_student(request):
    return Student.objects.get(user=request.user)

def create_invoice(booking, hourly_cost):

    user = Student.objects.get(user__email=booking.user)

    invoice_number = generate_invoice_number(user)

    #Calculate amount to pay
    total_required = (float(hourly_cost) * booking.number_of_lessons * booking.duration_of_lessons / 60)

    #Create invoice
    invoice = Invoice.objects.create(
        invoice_number=invoice_number,
        student=user,
        full_amount=total_required,
        paid_amount=0,
        fully_paid=False
    )
    invoice.full_clean()
    invoice.save()

    return invoice_number

def generate_invoice_number(user):
    invoice_number = ""
    user_id = user.id
    number_of_invoices_for_user = Invoice.objects.all().filter(student=user).count() + 1
    for i in range(4-len(str(user_id))):
        invoice_number += "0"
    invoice_number = invoice_number + str(user_id) + "-"
    for i in range(3-len(str(number_of_invoices_for_user))):
        invoice_number += "0"
    invoice_number += str(number_of_invoices_for_user)
    return invoice_number

def get_user(form):
    email = form.cleaned_data.get('email')
    password = form.cleaned_data.get('password')
    return authenticate(email=email, password=password)

def term_name_already_exists(old_term_name, new_term_name):
    # Run if there has been a change to the term name
    if old_term_name != new_term_name:
        current_school_terms = SchoolTerm.objects.all()

        for term in current_school_terms:
            # If the new name is the same as any existing names:
            if term.term_name == new_term_name:
                return True

    return False

def get_redirect_url_for_user(user):
    if user.get_group() == "Student":
        return settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT
    elif user.get_group() == "Admin":
        return settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_ADMIN
    elif user.get_group() == 'Director':
        return settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_DIRECTOR
    else:
        return ''

def get_invoice_list(request):
    try:
        r_user = request.user
        r_student = Student.objects.get(user=r_user)
        invoices = Invoice.objects.all().filter(student=r_student).reverse()
        return invoices
    except ObjectDoesNotExist:
        return Invoice.objects.none()
    

def get_transaction_list(request):
    try:
        r_user = request.user
        r_student = Student.objects.get(user=r_user)
        transactions = BankTransaction.objects.order_by('date').filter(student=r_student)
        return transactions
    except ObjectDoesNotExist:
        return BankTransaction.objects.none()

def redirect_to_invoice_list(user):
    if user.is_admin_or_director():
        return redirect('invoice_list_admin')
    else:
        return redirect('invoice_list_student')

def redirect_to_request_list(user, relation_id):
    if user.is_admin_or_director():
        return redirect('admin_request_list')
    elif is_child(relation_id):
        return redirect_with_queries('child_request_list', relation_id=relation_id)
    else:
        return redirect('request_list')

def generate_lessons_from_bookings(bookings):
    lesson_list = []

    for booking in bookings:
        term = booking.term_id
        date = booking.start_date
        lesson_datetime = datetime.datetime.combine(date, booking.time_of_the_day) #perhaps do not generate lesson in list if this date is in the past
        duration = Booking.LessonDuration.choices[
                Booking.LessonDuration.values.index(booking.duration_of_lessons)
            ]

        for lesson_num in range(booking.number_of_lessons):
            if lesson_datetime >= datetime.datetime.today():
                lesson = Lesson(
                    booking,
                    lesson_datetime,
                    get_full_name_by_relation_id(booking.user, booking.relation_id),
                    booking.teacher,
                    str(booking.duration_of_lessons) + " mins",
                    booking.further_information
                )

                lesson_list.append(lesson)

            lesson_datetime += datetime.timedelta(days=booking.interval_between_lessons)

    lesson_list.sort(key=lambda x: x.date_time, reverse = True)

    return lesson_list

def check_if_lessons_not_in_termtime(lessons):
    for lesson in lessons:
        if find_term_from_date_allow_none(lesson.date_time) == None:
            return True

    return False

def user_authorised_to_see_invoice(request, invoice_id):
    '''Checks if user sending the request is allowed to see the invoice'''
    if request.user.is_admin_or_director(): return True

    invoice_object = get_invoice_object(invoice_id)
    student_object = get_student(request)

    return invoice_object.student == student_object

def child_exists(relation_id):
    '''Checks if a child with given relation id exists'''
    return Child.objects.filter(id=relation_id).exists()

def user_is_parent(request, relation_id):
    '''Checks if the user sending the request is the parent of the given relation id'''
    child = get_child_object(relation_id)
    return request.user == child.parent