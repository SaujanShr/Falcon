from django.core.management.base import BaseCommand, CommandError
from lessons.models import User,SchoolTerm,DayOfTheWeek,Request,Student,Booking, BankTransaction,Invoice,Child

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Unseeding data...")
        User.objects.all().delete()
        SchoolTerm.objects.all().delete()
        DayOfTheWeek.objects.all().delete()
        Request.objects.all().delete()
        Student.objects.all().delete()
        Booking.objects.all().delete()
        BankTransaction.objects.all().delete()
        Invoice.objects.all().delete()
        Child.objects.all().delete()
        print("Done!")