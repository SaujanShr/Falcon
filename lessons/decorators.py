from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponse

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            if (request.user.groups.all()[0].name == 'Student'):
                    user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_STUDENT
            elif (request.user.groups.all()[0].name == 'Admin'):
                user_specific_redirect = settings.REDIRECT_URL_WHEN_LOGGED_IN_FOR_ADMIN
            return redirect(user_specific_redirect)
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
                return view_function(request)
            else:
                if group == 'Admin':
                    return redirect('redirect')
                elif group == 'Student':
                    return redirect('student_page')
                else:
                    return HttpResponse("pb")
        return wrapper
    return decorator