from .models import Request, Student, Child, SchoolTerm
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
        date_user_request_pairs.append({'date':str(user_request.date), 
                                        'request':user_request})
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
    return form.save()


def get_new_request_view_form(request):
    this_request = get_request_object(request)
    form = RequestViewForm(
        initial={
            'date':this_request.date,
            'student_name':this_request.student_name,
            'availability':this_request.availability.all(),
            'number_of_lessons':this_request.number_of_lessons,
            'interval_between_lessons':this_request.interval_between_lessons,
            'duration_of_lessons':this_request.duration_of_lessons,
            'further_information':this_request.further_information,
            'fulfilled':this_request.fulfilled
            },
        user=this_request.user
        )
    return form

def get_student(request):
    return Student.objects.get(user=request.user)

def get_child(request):
    full_name = request.full_name
    return Child.objects.filter(parent=request.user,full_name=full_name)[0]

def get_children(request):
    return Child.objects.filter(parent=request.user)


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



