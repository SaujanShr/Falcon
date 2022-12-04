import decimal
import urllib
from django.utils import timezone
from .models import Request, Invoice, Student, Child, Booking, DayOfTheWeek, SchoolTerm, BankTransaction
from .forms import RequestForm, FulfilRequestForm, EditBookingForm, ChildViewForm, TransactionSubmitForm, InvoiceViewForm
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import redirect

def redirect_with_queries(url, **queries):
    response = redirect(url)
    if queries:
        query_string = urllib.parse.urlencode(queries)
        response['location'] += '?' + query_string
    return response

def get_prev_url_from_request(request):
    if request.method == 'GET':
        return request.GET.get('prev_url', None)
    elif request.method == 'POST':
        return request.POST.get('prev_url', None)
    return None

def get_invoice_id_from_request(request):
    if request.method == 'GET':
        return request.GET.get('invoice_id', None)
    elif request.method == 'POST':
        return request.POST.get('invoice_id', None)
    return None

def get_invoice_object(invoice_id):
    return Invoice.objects.get(invoice_number=invoice_id)

def get_invoice_object_from_request(request):
    return get_invoice_object(get_invoice_id_from_request(request))

def get_request_object(request_id):
    return Request.objects.get(id=request_id)

def get_booking_object(booking_id):
    return Booking.objects.get(invoice_id=booking_id)

def get_child_object(relation_id):
    return Child.objects.get(id=relation_id)
    
def get_student_balance(request):
    user = request.user
    try:
        student = Student.objects.get(user=user)
        return student.balance
    except ObjectDoesNotExist:
        return None

def get_invoice_object(invoice_number):
    return Invoice.objects.get(invoice_number=invoice_number)

def get_request_id_from_request(request):
    if request.method == 'GET':
        return request.GET.get('request_id', None)
    elif request.method == 'POST':
        return request.POST.get('request_id', None)
    return None

def get_relation_id_from_request(request):
    if request.method == 'GET':
        return request.GET.get('relation_id', -1)
    elif request.method == 'POST':
        return request.POST.get('relation_id', -1)
    return None

def get_booking_id_from_request(request):
    if request.method == 'GET':
        return request.GET.get('booking_id', None)
    elif request.method == 'POST':
        return request.POST.get('booking_id', None)
    return None

def get_request_object_from_request(request):
    return get_request_object(get_request_id_from_request(request))

def get_child_object_from_request(request):
    return get_child_object(get_relation_id_from_request(request))

def get_booking_object_from_request(request):
    return get_booking_object(get_booking_id_from_request(request))

def is_child(relation_id):
    return int(relation_id) != -1

def get_client_from_relation_id(user, relation_id):
    if is_child(relation_id):
        return Child.objects.get(id=relation_id)
    else:
        return user

def get_request_objects(user, relation_id = -1):
    return Request.objects.filter(user=user, relation_id=relation_id).order_by('-date')

def delete_request_object_from_request(request):
    return get_request_object_from_request(request).delete()

def update_request_object_from_request(request):
    user_request = get_request_object_from_request(request)
    data = request.POST
    
    form = RequestForm(instance_id=user_request.id, data=data)
    
    if form.is_valid():
        return form.save()

def get_booking_objects(user, relation_id = -1):
    return Booking.objects.filter(user=user, relation_id=relation_id).order_by('start_date')

def get_full_name(student):
    return f'{student.first_name} {student.last_name}'

def get_full_name_by_relation_id(user, relation_id):
    if is_child(relation_id):
        child = get_child_object(relation_id)
        return get_full_name(child)
    else:
        return get_full_name(user)

def get_child_idname(relation_id):
    child = get_child_object(relation_id)
    return {'id':child.id, 'name':get_full_name(child)}

def get_children(user):
    return Child.objects.filter(parent=user)

def get_children_idname(user):
    children = get_children(user)
    children_idname = []
    for child in children:
        children_idname.append(get_child_idname(child.id))
    return children_idname

def delete_child(user, relation_id):
    get_request_objects(user, relation_id).delete()
    bookings = get_booking_objects(user, relation_id)
    for booking in bookings:
        refund_booking_if_valid(booking)
    bookings.delete()
        
    return get_child_object(relation_id).delete()

def update_child_object_from_request(request):
    child = get_child_object_from_request(request)
    data = request.POST
    
    form = ChildViewForm(instance_id=child.id, data=data)
    if form.is_valid():
        return form.save()

def format_request_for_display(request: Request):
    request.interval_between_lessons = Request.IntervalBetweenLessons.choices[
        Request.IntervalBetweenLessons.values.index(request.interval_between_lessons)
    ]
    Request.IntervalBetweenLessons._member_names_
    request.duration_of_lessons = request.LessonDuration.choices[
        request.LessonDuration.values.index(request.duration_of_lessons)
    ]
    request.raw_date = str(request.date).split()[0]
    request.student_name = get_full_name_by_relation_id(request.user, request.relation_id)
    
    return request

def get_and_format_requests_for_display(user, relation_id=-1):
    requests = get_request_objects(user, relation_id)
    formatted_requests = []
    
    for request in requests:
        formatted_requests.append(format_request_for_display(request))
    
    return formatted_requests

def get_and_format_requests_for_admin_display():
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
    booking.interval_between_lessons = Booking.IntervalBetweenLessons.choices[
        Booking.IntervalBetweenLessons.values.index(booking.interval_between_lessons)
    ]
    booking.duration_of_lessons = Booking.LessonDuration.choices[
        Booking.LessonDuration.values.index(booking.duration_of_lessons)
    ]
    booking.raw_date = str(booking.start_date).split()[0]
    booking.student_name = get_full_name_by_relation_id(booking.user, booking.relation_id)
    
    return booking

def get_and_format_bookings_for_display(user, relation_id=-1):
    bookings = get_booking_objects(user, relation_id)
    formatted_bookings = []
    
    for booking in bookings:
        formatted_bookings.append(format_booking_for_display(booking))
    
    return formatted_bookings

def get_and_format_bookings_for_admin_display():
    bookings = Booking.objects.all()
    formatted_bookings = []

    for booking in bookings:
        formatted_bookings.append(format_booking_for_display(booking))
    
    return formatted_bookings


def refund_booking_if_valid(booking: Booking):
    if booking.start_date >= timezone.now().date():
        return
    
    invoice = get_invoice_object(booking.invoice_id)
    student = Student.objects.get(user=booking.user)
    student.balance += invoice.paid_amount
    invoice.paid_amount = 0
    invoice.full_amount = 0
    invoice.fully_paid = True
    invoice.save()
    student.save()

def update_booking(request):
    data = request.POST.copy()
    booking = get_booking_object_from_request(request)
    print(data['invoice_id'])
    booking.day_of_the_week = DayOfTheWeek.objects.get(order=(int(data['day_of_the_week'])-1))
    booking.time_of_the_day = data['time_of_the_day']
    booking.teacher = data['teacher']
    booking.start_date = data['start_date']
    booking.duration_of_lessons = data['duration_of_lessons']
    booking.interval_between_lessons = data['interval_between_lessons']
    booking.number_of_lessons = data['number_of_lessons']
    booking.further_information = data['further_information']
    booking.full_clean()

    #Update invoice
    student = Student.objects.get(user=booking.user)
    invoice = Invoice.objects.get(invoice_number=data['invoice_id'])
    new_cost = booking.duration_of_lessons * int(data['hourly_cost']) * booking.number_of_lessons / 60
    invoice.full_amount = new_cost

    if invoice.paid_amount > invoice.full_amount:
        student.balance = student.balance + decimal.Decimal((invoice.paid_amount-decimal.Decimal(invoice.full_amount)))
        invoice.paid_amount = invoice.full_amount
        invoice.fully_paid = True
        student.save()
    elif invoice.paid_amount == invoice.full_amount:
        invoice.fully_paid = True
    else:
        invoice.fully_paid = False

    invoice.save()
    booking.save()
    
    return booking

def delete_booking(request):
    data = request.POST
    booking = get_booking_object_from_request(request)
    refund_booking_if_valid(booking)
    
    return booking.delete()

def get_booking_form(booking_id):
    booking = get_booking_object(booking_id)
    invoice = Invoice.objects.get(invoice_number=booking.invoice_id)
    hourly_cost = int(invoice.full_amount/booking.duration_of_lessons/booking.number_of_lessons*60)
    form = EditBookingForm(
        initial={
            'invoice_id': booking.invoice_id,
            'day_of_the_week': booking.day_of_the_week,
            'time_of_the_day': booking.time_of_the_day,
            'teacher': booking.teacher,
            'start_date': booking.start_date,
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
    form = ChildViewForm(
        initial={
            'first_name':child.first_name,
            'last_name':child.last_name
        }
    )
    return form

def get_invoice_view_form(invoice_id):
    invoice = get_invoice_object(invoice_id)
    #['invoice_number', 'student', 'full_amount', 'paid_amount', 'fully_paid']
    form = InvoiceViewForm(
        initial={
            'invoice_number':invoice.invoice_number,
            'student_name': invoice.student.user.email,
            'full_amount': invoice.full_amount,
            'paid_amount': invoice.paid_amount,
            'fully_paid': invoice.fully_paid
        }
    )

    return form


def get_request_view_form(request_id):
    user_request = get_request_object(request_id)

    form = RequestForm(
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

def get_fulfil_request_form(request):
    this_request = get_request_object_from_request(request)
    form = FulfilRequestForm(
        initial={
            'date': this_request.date,
            'number_of_lessons': this_request.number_of_lessons,
            'interval_between_lessons': this_request.interval_between_lessons,
            'duration_of_lessons': this_request.duration_of_lessons,
            'further_information': this_request.further_information
        },
        reqe=this_request
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
    if user.is_admin():
        return redirect('invoice_list_admin')
    else:
        return redirect('invoice_list_student')

def redirect_to_request_list(user, relation_id):
    if user.is_admin():
        return redirect('admin_request_list')
    elif is_child(relation_id):
        return redirect_with_queries('child_request_list', relation_id=relation_id)
    else:
        return redirect('request_list')