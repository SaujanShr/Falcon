from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from microblogs.models import User


class Command(BaseCommand):
    PASSWORD = "Password123"
    USER_COUNT = 100

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        user_count = 0
        while user_count < Command.USER_COUNT:
            print(f'Seeding user {user_count}',  end='\r')
            try:
                self.create_mandatory_users()
                self._create_random_users()
            except (django.db.utils.IntegrityError):
                continue
            user_count += 1
        print('User seeding complete')

    def create_mandatory_users(self):
        users = [{'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@example.org', 'password': Command.PASSWORD},
            {'first_name': 'Petra', 'last_name': 'Pickles',
                'email': 'petra.pickles@example.org', 'password': Command.PASSWORD},
            {'first_name': 'Marty', 'last_name': 'Major', 'email': 'marty.major@example.org', 'password': Command.PASSWORD}]

        for user in users:
            User.objects.create_user(
                user['email'], 
                first_name=user['first_name'],
                last_name=user['last_name'], 
                password=user['password']
            )

        student_user = User.objects.get(email="john.doe@example.org")
        student_group = Group.objects.get(name='Student') 
        student_group.user_set.add(student_user)     
        
        admin_user = User.objects.get(email="petra.pickles@example.org")
        student_group = Group.objects.get(name='Admin') 
        student_group.user_set.add(admin_user)    

        director_user = User.objects.get(email="john.doe@example.org")
        director_user.is_staff = True
        director_user.is_superuser = True

  

    def _email(self, first_name, last_name):
        email = f'{first_name}.{last_name}@example.org'
        return email

    def _username(self, first_name, last_name):
        username = f'@{first_name}{last_name}'
        return username
