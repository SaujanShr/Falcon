from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from faker import Faker
from lessons.models import BankTransaction, User, Student, SchoolTerm, DayOfTheWeek, Request
import datetime


class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        
    def handle(self, *args, **options):
        if Group.objects.count() == 0:
            GROUPS_PERMISSIONS = {
                'Admin': {
                    BankTransaction: ['add', 'change', 'delete', 'view'],
                    Request: ['change', 'delete', 'view'],
                    User: ['add', 'change', 'delete', 'view'],
                },
                'Student': {
                    BankTransaction: ['add', 'change', 'delete', 'view'],
                    Request: ['add', 'change', 'delete', 'view'],
                    User: ['add', 'change', 'delete', 'view'],
                },
            }
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
            
        
        #Seed Users
        print('Seeding data...')
        student_group = Group.objects.get(name='Student')
        student = User.objects.create_user(email='john.doe@example.org', password='Password123', first_name='John', last_name='Doe')
        student_group.user_set.add(student)
        Student.objects.create(user=student)

        admin_group = Group.objects.get(name='Admin')
        admin = User.objects.create_user(email='petra.pickles@example.org', password='Password123', first_name='Petra', last_name='Pickles')
        admin_group.user_set.add(admin)

        director = User.objects.create_superuser(email='marty.major@example.org', password='Password123', first_name='Marty', last_name='Major')
        print('Done.')

        # Seed School Terms
        if SchoolTerm.objects.count() == 0:
            print("Creating Terms...")
            SchoolTerm(term_name="Term one", start_date=datetime.date(2022, 9, 1), end_date=datetime.date(2022, 10, 21)).save()
            SchoolTerm(term_name="Term two", start_date=datetime.date(2022, 10, 31), end_date=datetime.date(2022, 12, 16)).save()
            SchoolTerm(term_name="Term three", start_date=datetime.date(2023, 1, 3), end_date=datetime.date(2023, 2, 10)).save()
            SchoolTerm(term_name="Term four", start_date=datetime.date(2023, 2, 20), end_date=datetime.date(2023, 3, 31)).save()
            SchoolTerm(term_name="Term five", start_date=datetime.date(2023, 4, 17), end_date=datetime.date(2023, 5, 26)).save()
            SchoolTerm(term_name="Term six", start_date=datetime.date(2023, 6, 5), end_date=datetime.date(2023, 7, 21)).save()
            print("Created.")
        else:
            print("Terms already exist")

        # Seed Days of the week
        if DayOfTheWeek.objects.count() == 0:
            print("Creating 7 days of the week...")
            DayOfTheWeek.objects.create(order=0, day=DayOfTheWeek.Day.MONDAY)
            DayOfTheWeek.objects.create(order=1, day=DayOfTheWeek.Day.TUESDAY)
            DayOfTheWeek.objects.create(order=2, day=DayOfTheWeek.Day.WEDNESDAY)
            DayOfTheWeek.objects.create(order=3, day=DayOfTheWeek.Day.THURSDAY)
            DayOfTheWeek.objects.create(order=4, day=DayOfTheWeek.Day.FRIDAY)
            DayOfTheWeek.objects.create(order=5, day=DayOfTheWeek.Day.SATURDAY)
            DayOfTheWeek.objects.create(order=6, day=DayOfTheWeek.Day.SUNDAY)
            print("Created.")
        else:
            print("Days already exist")

