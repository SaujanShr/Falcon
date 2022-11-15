from .models import Request
from .forms import RequestViewForm

def get_user_requests(request_user):
    return Request.objects.filter(user=request_user)

def delete_request(request_data):
    Request.objects.get(date=request_data['date']).delete()

def update_request(request_data):
    Request.objects.get(date=request_data['date']).delete()
    request_data.save()

def get_request_view_form(request_data):
    this_request = Request.objects.get(date=request_data['date'])
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