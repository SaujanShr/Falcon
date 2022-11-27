import decimal
from .models import Request, Invoice, Student, Child, User, Booking, DayOfTheWeek, SchoolTerm
from .forms import RequestViewForm, NewRequestViewForm
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone


def get_request_object(request) -> Request:
    if request.method == 'GET':
        return Request.objects.get(date=request.GET['date'])
    elif request.method == 'POST':
        return Request.objects.get(date=request.POST['date'])
    return None


def get_user_requests(request, name=None):
    user = request.user
    
    if name: return Request.objects.filter(user=user, student_name=name).order_by('-date')
    return Request.objects.filter(user=user).order_by('-date')


def get_date_user_request_pairs(request, name=None):
    user_requests = get_user_requests(request, name)
    
    date_user_request_pairs = []
    for user_request in user_requests:
        date_user_request_pairs.append({'date': str(user_request.date),
                                        'request': user_request})
    return date_user_request_pairs


def delete_request(request):
    return get_request_object(request).delete()


def update_request(request):
    user_request = get_request_object(request)

    # Can't update a fulfilled request.
    if user_request.fulfilled:
        return None
    
    post_data = request.POST.copy()
    post_data['date'] = user_request.date
    post_data['fulfilled'] = user_request.fulfilled

    request_instance = Request.objects.get(date=post_data['date'])

    form = RequestViewForm(request.user, post_data, instance=request_instance)
    return form.save()

def save_new_request(request):
    form = NewRequestViewForm(request.user, request.POST)
    if form.is_valid():
        return form.save()


def update_booking(request):
    data = request.POST.copy()
    booking = Booking.objects.get(invoice_id=data['invoice_id'])
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



def delete_booking(request):
    #This delete function will return any money paid
    data = request.POST.copy()
    booking = Booking.objects.get(invoice_id=data['invoice_id'])
    invoice = Invoice.objects.get(invoice_number=data['invoice_id'])
    student = Student.objects.get(user=booking.user)
    student.balance = student.balance + invoice.paid_amount
    invoice.paid_amount = 0
    invoice.full_amount = 0
    invoice.fully_paid = True
    invoice.save()
    booking.delete()
    student.save()





def get_booking_form(request):
    booking = Booking.objects.get(invoice_id=request.GET['inv_id'])
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

def get_new_request_view_form(request):

    this_request = get_request_object(request)
    form = RequestViewForm(
        initial={
            'date':this_request.date,
            'student_name':this_request.student_name,
            'availability':this_request.availability.all().first(),
            'number_of_lessons':this_request.number_of_lessons,
            'interval_between_lessons':this_request.interval_between_lessons,
            'duration_of_lessons':this_request.duration_of_lessons,
            'further_information':this_request.further_information,
            'fulfilled':this_request.fulfilled
            },
        user=this_request.user
        )
    return form


def get_fulfil_request_form(request):
    this_request = get_request_object(request)
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

def get_child(request):
    full_name = request.full_name
    return Child.objects.filter(parent=request.user,full_name=full_name)[0]

def get_children(request):
    return Child.objects.filter(parent=request.user)


def create_invoice(booking, hourly_cost):


    user = Student.objects.get(user__email=booking.user)


    #Generate invoice number
    invoice_n = ""
    user_id = user.id
    number_of_invoice = Invoice.objects.all().filter(student=user).count() + 1
    for i in range(4-len(str(user_id))):
        invoice_n += "0"
    invoice_n = invoice_n + str(user_id) + "-"
    for i in range(3-len(str(number_of_invoice))):
        invoice_n += "0"
    invoice_n += str(number_of_invoice)

    #Calculate amount to pay
    total_required = (int(hourly_cost) * booking.number_of_lessons * booking.duration_of_lessons / 60)
    amount_paid = 0
    paid_in_full = (total_required == 0)

    #Create invoice
    invoice = Invoice.objects.create(
        invoice_number=invoice_n,
        student=user,
        full_amount=total_required,
        paid_amount=amount_paid,
        fully_paid=paid_in_full
    )
    invoice.full_clean()
    invoice.save()

    return invoice_n


def get_redirect_url(user, request):
    if user.groups.exists():
        if (user.groups.all()[0].name == 'Student'):
            user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT
        elif (user.groups.all()[0].name == 'Admin'):
            user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_ADMIN
    else:
        if user.is_staff:
            user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_DIRECTOR
        else:
            user_specific_redirect = ''
    return request.POST.get('next') or user_specific_redirect


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



