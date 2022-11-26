from .models import Request, Student, Child
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
    get_request_object(request).delete()
    return True


def update_request(request):
    user_request = get_request_object(request)

    # Can't update a fulfilled request.
    if user_request.fulfilled:
        return None
    
    data = request.POST.copy()
    data['date'] = user_request.date
    data['user'] = user_request.user
    data['fulfilled'] = user_request.fulfilled
    user_request.delete()
    
    form = RequestViewForm(data)
    form.fields['date'].disabled = False
    form.fields['fulfilled'].disabled = False
    
    if form.is_valid():
        return form.save()
    
    print(form.errors)
    return None

def save_new_request(request):
    data = request.POST.copy()
    data['date'] = timezone.datetime.now(tz=timezone.utc)
    data['user'] = request.user
    
    form = NewRequestViewForm(data)
    print("date:",form.fields['date'])
    
    if form.is_valid():
        return form.save()
    
    print(form.errors)
    return None


def get_request_view_form(request):
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
            }
        )
    return form

def get_student(request):
    return Student.objects.get(user=request.user)

def get_child(request):
    first_name = request.first_name
    last_name = request.last_name
    return Child.objects.filter(parent=request.user,first_name=first_name,last_name=last_name)[0]

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

