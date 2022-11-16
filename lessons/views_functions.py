from .models import Request
from .forms import RequestViewForm

def get_request_object(request) -> Request:
    if request.method == 'GET':
        return Request.objects.get(date=request.GET['date'])
    elif request.method == 'POST':
        return Request.objects.get(date=request.POST['date'])
    
    return None

def get_user_requests(request):
    user = request.user
    return Request.objects.filter(user=user)

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
    form = get_request_view_form(request)
    form.user = request.user
    #delete_request(request)
    
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