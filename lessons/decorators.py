from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            user_specific_redirect = ''
            if request.user.groups.exists():
                if (request.user.groups.all()[0].name == 'Student'):
                        user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT
                elif (request.user.groups.all()[0].name == 'Admin'):
                    user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_ADMIN
            elif request.user.is_staff:
                user_specific_redirect = (settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_DIRECTOR)
            return redirect(user_specific_redirect)
        else:
            return view_function(request)
            # execute
    return modified_view_function

def allowed_groups(allowed_groups_names = []):
    def decorator(view_function):
        def wrapper(request, *args, **kwargs):
            group = None
            if request.user.is_superuser:
                group = 'Director'
            elif request.user.is_admin():
                group = 'Admin'
            elif request.user.is_student():
                group = 'Student'

            if group in allowed_groups_names:
                return view_function(request,*args,**kwargs)
            else:
                if group == 'Admin':
                    return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_ADMIN)
                elif group == 'Student':
                    return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT)
                elif group == 'Director':
                    return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_DIRECTOR)
                else:
                    return HttpResponse("ERROR: you attempted to access a forbidden page. Your account will be submitted for review by our security team.")
        return wrapper
    return decorator