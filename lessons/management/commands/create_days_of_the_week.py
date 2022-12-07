from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group,Permission
from lessons.models import DayOfTheWeek

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        
    def handle(self, *args, **options):
        if DayOfTheWeek.objects.exists():
            return
        
        DayOfTheWeek.objects.create(order=0, day=DayOfTheWeek.Day.MONDAY)
        DayOfTheWeek.objects.create(order=1, day=DayOfTheWeek.Day.TUESDAY)
        DayOfTheWeek.objects.create(order=2, day=DayOfTheWeek.Day.WEDNESDAY)
        DayOfTheWeek.objects.create(order=3, day=DayOfTheWeek.Day.THURSDAY)
        DayOfTheWeek.objects.create(order=4, day=DayOfTheWeek.Day.FRIDAY)
        DayOfTheWeek.objects.create(order=5, day=DayOfTheWeek.Day.SATURDAY)
        DayOfTheWeek.objects.create(order=6, day=DayOfTheWeek.Day.SUNDAY)