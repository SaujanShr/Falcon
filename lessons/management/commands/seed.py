from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from faker import Faker
from lessons.models import User, Student

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        
    def handle(self, *args, **options):
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

