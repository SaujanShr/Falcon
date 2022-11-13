from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
            # execute
    return modified_view_function

def allowed_groups(allowed_groups_names = []):
    def decorator(view_function):
        def wrapper(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            
            if group in allowed_groups_names:
                return view_func(request,*args,**kwargs)
            else:
                return HttpResponse("ERROR 404: We can create an Error 404 Page")
        return wrapper
    return decorator