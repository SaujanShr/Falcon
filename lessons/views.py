from django.shortcuts import render
from .models import Request

def student_page(request):
    requests = Request.objects.filter(student_id=1)
    return render(request, 'student_page.html', {'requests':requests})