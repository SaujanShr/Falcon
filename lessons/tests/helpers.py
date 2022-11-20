from django.urls import reverse
from lessons.models import User, DayOfTheWeek
from django.contrib.auth.models import Group, Permission
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


def create_days_of_the_week():
    DayOfTheWeek.objects.create(order=0, day=DayOfTheWeek.Day.MONDAY)
    DayOfTheWeek.objects.create(order=1, day=DayOfTheWeek.Day.TUESDAY)
    DayOfTheWeek.objects.create(order=2, day=DayOfTheWeek.Day.WEDNESDAY)
    DayOfTheWeek.objects.create(order=3, day=DayOfTheWeek.Day.THURSDAY)
    DayOfTheWeek.objects.create(order=4, day=DayOfTheWeek.Day.FRIDAY)
    DayOfTheWeek.objects.create(order=5, day=DayOfTheWeek.Day.SATURDAY)
    DayOfTheWeek.objects.create(order=6, day=DayOfTheWeek.Day.SUNDAY)


class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()


class HandleGroups:

    def set_default_user_to_student():
        create_user_groups()
        default_user = User.objects.get(email='johndoe@email.com')
        student_group = Group.objects.get(name='Student')
        student_group.user_set.add(default_user)

    def set_other_user_to_admin():
        create_user_groups()
        other_user = User.objects.get(email='janedoe@email.com')
        admin_group = Group.objects.get(name='Admin')
        admin_group.user_set.add(other_user)


