from django.contrib.auth.models import Group,Permission
from . import models

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

def check_initialization():
    if not groups_exist():
        create_groups()
        
def groups_exist():
    return Group.objects.count() > 0

def create_groups():
    for group_name in GROUPS_PERMISSIONS:

        group, created = Group.objects.get_or_create(name=group_name)

        for authorization in GROUPS_PERMISSIONS[group_name]:

            for permission_index, permission_name in enumerate(GROUPS_PERMISSIONS[group_name][authorization]):
                permission_codename = permission_name + "_" + authorization._meta.model_name
                try:
                    permission = Permission.objects.get(codename=permission_codename)
                    group.permissions.add(permission)
                    print("Adding "
                                      + permission_codename
                                      + " to group "
                                      + group.__str__())
                except Permission.DoesNotExist:
                    print(permission_codename + " not found")