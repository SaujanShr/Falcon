from django.shortcuts import render
from .models import Request, Booking, DayOfTheWeek, User #TODO: remove dayoftheweek
from .forms import RequestViewForm

def student_page(request):
    requests = Request.objects.all()
    return render(request, 'student_page.html', {'requests':requests})

def request_view(request):
    if request.method == 'GET':
        this_request = Request.objects.get(date=request.GET['date'])
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
        return render(request, 'request_view.html', {'form':form})

def admin_bookings_requests_view(request):
    if request.method == 'GET':
        requests = Request.objects.all()
        bookings = Booking.objects.all()
        return render(request, 'admin_view_requests.html', {'requests': requests,
                                                            'bookings': bookings})

