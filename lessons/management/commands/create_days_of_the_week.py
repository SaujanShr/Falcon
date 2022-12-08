from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group,Permission
from lessons.models import DayOfTheWeek

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        
    def handle(self, *args, **options):
        if DayOfTheWeek.objects.exists():
            DayOfTheWeek.objects.all().delete()
        
        DayOfTheWeek.objects.create(order=0, day=DayOfTheWeek.Day.MONDAY)
        print('Monday created!')
        DayOfTheWeek.objects.create(order=1, day=DayOfTheWeek.Day.TUESDAY)
        print('Tuesday created!')
        DayOfTheWeek.objects.create(order=2, day=DayOfTheWeek.Day.WEDNESDAY)
        print('Wednesday created!')
        DayOfTheWeek.objects.create(order=3, day=DayOfTheWeek.Day.THURSDAY)
        print('Thursday created!')
        DayOfTheWeek.objects.create(order=4, day=DayOfTheWeek.Day.FRIDAY)
        print('Friday created!')
        DayOfTheWeek.objects.create(order=5, day=DayOfTheWeek.Day.SATURDAY)
        print('Saturday created!')
        DayOfTheWeek.objects.create(order=6, day=DayOfTheWeek.Day.SUNDAY)
        print('Sunday created!')