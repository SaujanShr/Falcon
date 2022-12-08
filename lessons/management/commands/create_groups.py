from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group,Permission
from lessons import models

class Command(BaseCommand):
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
    def __init__(self):
        super().__init__()
        
    def handle(self, *args, **options):
        for group_name in self.GROUPS_PERMISSIONS:
            group, created = Group.objects.get_or_create(name=group_name)
            for authorization in self.GROUPS_PERMISSIONS[group_name]:
                for permission_index, permission_name in enumerate(self.GROUPS_PERMISSIONS[group_name][authorization]):
                    permission_codename = permission_name + "_" + authorization._meta.model_name
                    try:
                        permission = Permission.objects.get(codename=permission_codename)
                        group.permissions.add(permission)
                    except Permission.DoesNotExist:
                        print(permission_codename + " not found")