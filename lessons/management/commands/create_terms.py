import datetime
from django.core.management.base import BaseCommand
from lessons.models import SchoolTerm


class Command(BaseCommand):

    def __init__(self):
        super().__init__()

    def handle(self, *args, **options):
        if SchoolTerm.objects.count() == 0:
            print("Creating Terms")
            SchoolTerm(term_name="Term one", start_date=datetime.date(2022, 9, 1), end_date=datetime.date(2022, 10, 21)).save()
            SchoolTerm(term_name="Term two", start_date=datetime.date(2022, 10, 31), end_date=datetime.date(2022, 12, 16)).save()
            SchoolTerm(term_name="Term three", start_date=datetime.date(2023, 1, 3), end_date=datetime.date(2023, 2, 10)).save()
            SchoolTerm(term_name="Term four", start_date=datetime.date(2023, 2, 20), end_date=datetime.date(2023, 3, 31)).save()
            SchoolTerm(term_name="Term five", start_date=datetime.date(2023, 4, 17), end_date=datetime.date(2023, 5, 26)).save()
            SchoolTerm(term_name="Term six", start_date=datetime.date(2023, 6, 5), end_date=datetime.date(2023, 7, 21)).save()
            print("Created")
        else:
            print("Terms are already created")