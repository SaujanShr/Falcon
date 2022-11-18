from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import User
from django.contrib.auth.models import Group,Permission
from django.db.utils import IntegrityError

class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        self.create_mandatory_users()
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self._create_random_users()
            except (IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

    def create_mandatory_users(self):
        users = [{'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.org', 'password': Command.PASSWORD},
            {'first_name': 'Petra', 'last_name': 'Pickles',
                'email': 'petra.pickles@example.org', 'password': Command.PASSWORD},
            {'first_name': 'Marty', 'last_name': 'Major', 'email': 'marty.major@example.org', 'password': Command.PASSWORD}]

        for user in users:
            try:
                User.objects.create_user(
                    user['email'], 
                    first_name=user['first_name'],
                    last_name=user['last_name'], 
                    password=user['password']
                )
            except(IntegrityError):
                print(user['first_name'])

        student_user = User.objects.get(email="john.doe@example.org")
        student_group = Group.objects.get(name='Student') 
        student_group.user_set.add(student_user)     
        
        admin_user = User.objects.get(email="petra.pickles@example.org")
        student_group = Group.objects.get(name='Admin') 
        student_group.user_set.add(admin_user)    

        director_user = User.objects.get(email="john.doe@example.org")
        director_user.is_staff = True
        director_user.is_superuser = True

    def _create_random_users(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name, last_name)
        User.objects.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            password=Command.PASSWORD,
        )
        
    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email
