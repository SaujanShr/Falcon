from django.shortcuts import render
from .models import Request

def student_page(request):
    requests = Request.objects.all()
    return render(request, 'student_page.html', {'requests':requests})