from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from faker import Faker
from lessons.models import User, Student, SchoolTerm, DayOfTheWeek, Request
import datetime
from random import randint
from django.utils import timezone

class Command(BaseCommand):
    SCHOOL_TERMS = {
        "Term one":[datetime.date(2022, 9, 1),datetime.date(2022, 10, 21)],
        "Term two": [datetime.date(2022, 10, 31),datetime.date(2022, 12, 16)],
        "Term three":[datetime.date(2023, 1, 3),datetime.date(2023, 2, 10)],
        "Term four":[datetime.date(2023, 2, 20),datetime.date(2023, 3, 31)],
        "Term five":[datetime.date(2023, 4, 17),datetime.date(2023, 5, 26)],
        "Term six":[datetime.date(2023, 6, 5),datetime.date(2023, 7, 21)]
    }

    DAYS_OF_WEEK_CREATION_DATA = {
        DayOfTheWeek.Day.MONDAY:0,
        DayOfTheWeek.Day.TUESDAY:1,
        DayOfTheWeek.Day.WEDNESDAY:2,
        DayOfTheWeek.Day.THURSDAY:3,
        DayOfTheWeek.Day.FRIDAY:4,
        DayOfTheWeek.Day.SATURDAY:5,
        DayOfTheWeek.Day.SUNDAY:6
    }

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        
    def handle(self, *args, **options):
        #Seed Users
        print('Seeding data...')
        self._create_school_terms()
        created_days = self._create_days_of_the_week()
        self._create_required_records(created_days)
        print("Done!")
        

    def _create_school_terms(self):
        for term_name in self.SCHOOL_TERMS.keys():
            SchoolTerm(term_name=term_name, start_date=self.SCHOOL_TERMS[term_name][0], end_date=self.SCHOOL_TERMS[term_name][1]).save()

    def _create_days_of_the_week(self):
        create_days = []
        for day_of_the_week in self.DAYS_OF_WEEK_CREATION_DATA.keys():
            create_days.append(DayOfTheWeek.objects.create(order=self.DAYS_OF_WEEK_CREATION_DATA[day_of_the_week], day=day_of_the_week))
        return create_days

    def _create_required_records(self,created_days):
        self._create_required_users()
        self._create_requests_for_john_doe(created_days)

    def _create_required_users(self):
        student_group = Group.objects.get(name='Student')
        john_doe_user = User.objects.create_user(email='john.doe@example.org', password='Password123', first_name='John', last_name='Doe')
        student_group.user_set.add(john_doe_user)
        Student.objects.create(user=john_doe_user)

        admin_group = Group.objects.get(name='Admin')
        petra_pickles_user = User.objects.create_user(email='petra.pickles@example.org', password='Password123', first_name='Petra', last_name='Pickles')
        admin_group.user_set.add(petra_pickles_user)

        director = User.objects.create_superuser(email='marty.major@example.org', password='Password123', first_name='Marty', last_name='Major')
    
    def _create_requests_for_john_doe(self,created_days):
        john_doe_user =  User.objects.get(email='john.doe@example.org')
        john_doe_request = Request.objects.create(user=john_doe_user,student_name = john_doe_user.get_full_name(),number_of_lessons=randint(0,25),interval_between_lessons=1,duration_of_lessons=60,fulfilled=True,further_information='Lorem ipsum.',date=timezone.datetime.now(tz=timezone.utc))
        john_doe_request.availability.set([created_days[randint(0,len(created_days)-1)]])