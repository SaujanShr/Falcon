from django.shortcuts import render
from .models import Request
from .forms import RequestViewForm

def student_page(request):
    requests = Request.objects.all()
    date_requests = []
    for req in requests:
        date_requests.append([str(req.date), req])
        
    return render(request, 'student_page.html', {'date_requests':date_requests})

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