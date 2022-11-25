from .models import Request, SchoolTerm
from .forms import RequestViewForm
from django.conf import settings
from django.contrib.auth import authenticate
from datetime import datetime

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
        date_user_request_pairs.append({'date':str(user_request.date), 
                                        'request':user_request})
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
            'date':this_request.date,
            'availability':this_request.availability.all(),
            'number_of_lessons':this_request.number_of_lessons,
            'interval_between_lessons':this_request.interval_between_lessons,
            'duration_of_lessons':this_request.duration_of_lessons,
            'further_information':this_request.further_information,
            'fulfilled':this_request.fulfilled
            }
        )
    return form


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



