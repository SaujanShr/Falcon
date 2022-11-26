from .models import Request, Invoice, Student, User
from .forms import RequestViewForm, FulfilRequestForm
from django.conf import settings
from django.contrib.auth import authenticate


def get_request_object(request) -> Request:
    if request.method == 'GET':
        return Request.objects.get(date=request.GET['date'])
    elif request.method == 'POST':
        return Request.objects.get(date=request.POST['date'])

    return None


def get_user_requests(request):
    user = request.user
    return Request.objects.filter(user=user).order_by('-date')



def get_date_user_request_pairs(request):
    user_requests = get_user_requests(request)
    date_user_request_pairs = []
    for user_request in user_requests:
        date_user_request_pairs.append({'date': str(user_request.date),
                                        'request': user_request})
    return date_user_request_pairs


def delete_request(request):
    get_request_object(request).delete()


def update_request(request):
    user_request = get_request_object(request)

    # Can't update a fulfilled request.
    if user_request.fulfilled:
        return

    data = request.POST.copy()
    data['date'] = user_request.date
    data['user'] = user_request.user
    data['fulfilled'] = user_request.fulfilled
    user_request.delete()

    form = RequestViewForm(data)
    form.fields['date'].disabled = False
    form.fields['fulfilled'].disabled = False
    if form.is_valid():
        form.save()
    else:
        print(form.errors)


def get_request_view_form(request):

    this_request = get_request_object(request)
    form = RequestViewForm(
        initial={
            'date': this_request.date,
            'availability': this_request.availability.all().first(),
            'number_of_lessons': this_request.number_of_lessons,
            'interval_between_lessons': this_request.interval_between_lessons,
            'duration_of_lessons': this_request.duration_of_lessons,
            'further_information': this_request.further_information,
            'fulfilled': this_request.fulfilled
        }

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


def create_invoice(booking, hourly_cost):


    user = Student.objects.get(user__email=booking.student)


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


