from django.urls import reverse
from lessons.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Group,Permission
from lessons import models

GROUPS_PERMISSIONS = {
    'Admin': {
        models.BankTransaction: ['add', 'change', 'delete', 'view'],
        models.Request: ['change', 'delete', 'view'],
        models.User: ['add', 'change', 'delete', 'view'],
    },
    'Student': {
        models.BankTransaction: ['add', 'change', 'delete', 'view'],
        models.Request: ['add', 'change', 'delete', 'view'],
        models.User: ['add', 'change', 'delete', 'view'],
    },
}

def create_user_groups():
    for group_name in GROUPS_PERMISSIONS:
            group, created = Group.objects.get_or_create(name=group_name)
            for authorization in GROUPS_PERMISSIONS[group_name]:
                for permission_index, permission_name in enumerate(GROUPS_PERMISSIONS[group_name][authorization]):
                    permission_codename = permission_name + "_" + authorization._meta.model_name
                    try:
                        permission = Permission.objects.get(codename=permission_codename)
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        print(permission_codename + " not found")

def reverse_with_next(url_name, next_url):
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url

class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

class HandleGroups:

    def set_default_user_to_student():
        create_user_groups()
        default_user= User.objects.get(email='johndoe@email.com')
        student_group = Group.objects.get(name='Student') 
        student_group.user_set.add(default_user)
        
    def set_other_user_to_admin():
        create_user_groups()
        other_user = User.objects.get(email='janedoe@email.com')
        admin_group = Group.objects.get(name='Admin') 
        admin_group.user_set.add(other_user)