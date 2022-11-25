from .models import Request
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
            #'availability': this_request.availability.all(),
            'date': this_request.date,
            'number_of_lessons': this_request.number_of_lessons,
            'interval_between_lessons': this_request.interval_between_lessons,
            'duration_of_lessons': this_request.duration_of_lessons,
            'further_information': this_request.further_information
        },
        reqe=this_request
    )
    return form
