from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from faker import Faker
from lessons.models import User, Student, SchoolTerm, DayOfTheWeek, Request, Invoice, Booking, BankTransaction, Child
from datetime import datetime,date,timedelta
from django.utils import timezone
import pytz
from .create_groups import Command as GroupCreator
import random
from random import randint, sample

class Command(BaseCommand):

    PASSWORD_FOR_ALL = 'Password123'
    NUMBER_OF_STUDENTS_TO_CREATE = 100

    SCHOOL_TERMS = {
        "Term one":[date(2022, 9, 1),date(2022, 10, 21)],
        "Term two": [date(2022, 10, 31),date(2022, 12, 16)],
        "Term three":[date(2023, 1, 3),date(2023, 2, 10)],
        "Term four":[date(2023, 2, 20),date(2023, 3, 31)],
        "Term five":[date(2023, 4, 17),date(2023, 5, 26)],
        "Term six":[date(2023, 6, 5),date(2023, 7, 21)]
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

    DAYS_OF_THE_WEEK_INSTANCES = []

    LESSON_DURATIONS = [30,45,60]
    TIMES_BETWEEN_LESSONS = [7,14]

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        
    def handle(self, *args, **options):
        if not self.database_is_empty():
            print("WARNING: The database is currently not empty. Please unseed before attempting to seed again.")
        else:
            #Create groups  
            group_creator = GroupCreator()
            group_creator.handle()
            #Seed Users
            print('Seeding data...')
            self._create_school_terms()
            self._create_days_of_the_week()
            self._create_required_records()
            self._create_random_students_and_their_children()
            print("Done!")
        

    def _create_school_terms(self):
        for term_name in self.SCHOOL_TERMS.keys():
            SchoolTerm(term_name=term_name, start_date=self.SCHOOL_TERMS[term_name][0], end_date=self.SCHOOL_TERMS[term_name][1]).save()

    def _create_days_of_the_week(self):
        for day_of_the_week in self.DAYS_OF_WEEK_CREATION_DATA.keys():
            self.DAYS_OF_THE_WEEK_INSTANCES.append(DayOfTheWeek.objects.create(order=self.DAYS_OF_WEEK_CREATION_DATA[day_of_the_week], day=day_of_the_week))

    def _create_required_records(self):
        self._create_required_users()
        self._create_fulfilled_and_paid_request_for_john_doe()
        self._create_john_doe_children_and_their_paid_requests()

    def _create_john_doe_children_and_their_paid_requests(self):
        john_doe_user = User.objects.get(email='john.doe@example.org')
        alice_doe = self.create_child_for_user(john_doe_user,"Alice","Doe")
        bob_doe = self.create_child_for_user(john_doe_user,"Bob","Doe")
        alice_doe_request = self.create_random_request_for_user(john_doe_user,alice_doe.id,True)
        alice_doe_request.availability.set(sample(self.DAYS_OF_THE_WEEK_INSTANCES, randint(1,len(self.DAYS_OF_THE_WEEK_INSTANCES)-1)))
        alice_invoice = self._create_booking_for_request_and_return_invoice(alice_doe_request)
        self.pay_invoice(alice_invoice)
        bob_doe_request =self.create_random_request_for_user(john_doe_user,bob_doe.id,True)
        bob_doe_request.availability.set(sample(self.DAYS_OF_THE_WEEK_INSTANCES, randint(1,len(self.DAYS_OF_THE_WEEK_INSTANCES)-1)))
        bob_invoice = self._create_booking_for_request_and_return_invoice(bob_doe_request)
        self.pay_invoice(bob_invoice)

    def _create_required_users(self):
        student_group = Group.objects.get(name='Student')
        john_doe_user = User.objects.create_user(email='john.doe@example.org', password=self.PASSWORD_FOR_ALL, first_name='John', last_name='Doe')
        student_group.user_set.add(john_doe_user)
        Student.objects.create(user=john_doe_user)

        admin_group = Group.objects.get(name='Admin')
        petra_pickles_user = User.objects.create_user(email='petra.pickles@example.org', password=self.PASSWORD_FOR_ALL, first_name='Petra', last_name='Pickles')
        admin_group.user_set.add(petra_pickles_user)

        director = User.objects.create_superuser(email='marty.major@example.org', password=self.PASSWORD_FOR_ALL, first_name='Marty', last_name='Major')
    
    def _create_random_students_and_their_children(self):
        nb_students_created = 0
        while nb_students_created < self.NUMBER_OF_STUDENTS_TO_CREATE:
            _first_name = self.faker.first_name()
            _last_name = self.faker.last_name()
            created_user = User.objects.create_user(
                email=f"{_first_name.lower()}.{_last_name.lower()}@example.org", 
                password=self.PASSWORD_FOR_ALL, 
                first_name=_first_name, 
                last_name=_last_name)
            student_for_user = Student.objects.create(user=created_user)
            self.decide_and_create_request_for_random_user(created_user,-1)
            self.decide_and_create_child_for_random_user(created_user)
            nb_students_created += 1

    def decide_and_create_child_for_random_user(self,user):
        # Create a child for 90% of users
        if randint(0,10) <=9:
            child = self.create_child_for_user(user,self.faker.first_name(), self.faker.last_name())
            self.decide_and_create_request_for_random_user(user,child.id)
        # Create a second child for 70% of users (if no child as been created by previous block, it can be the first)
        if randint(0,10) <=7:
            child = self.create_child_for_user(user,self.faker.first_name(), self.faker.last_name())
            self.decide_and_create_request_for_random_user(user,child.id)

    def decide_and_create_request_for_random_user(self,random_user,relation_id):
        # Create requests for 95% of students in average.
        if randint(0,20) <= 19:
                user_request = self.create_random_request_for_user(random_user,relation_id,False)
                self.decide_and_fulfill_request_for_random_user(user_request)

    def decide_and_fulfill_request_for_random_user(self,request):
        # Fulfill 90% of requests in average.
        if randint(0,10) <=9:
            invoice = self._create_booking_for_request_and_return_invoice(request)
            request.fulfilled = True
            self.decide_and_pay_invoice_for_random_user(invoice)
    
    def decide_and_pay_invoice_for_random_user(self, invoice):
        pay_decider = randint(0,100)
        # Pay 45% of requests in average.
        if pay_decider <=45:
            self.pay_invoice(invoice)
        # Overpay 20% of requests in average.
        elif pay_decider <=65:
            self.overpay_invoice(invoice)
        # Partially pay 20% of requests in average.
        elif pay_decider <=85:
            self.underpay_invoice(invoice)
        #NOTE: 15% of requests in average will remain unpaid

    def create_random_request_for_user(self,user,relation_id,is_fulfilled):
        _interval_between_lessons=self.TIMES_BETWEEN_LESSONS[randint(0,len(self.TIMES_BETWEEN_LESSONS)-1)],
        term_of_the_lesson = random.choice(list(self.SCHOOL_TERMS))
        _date = pytz.timezone('UTC').localize(datetime.combine(self.faker.date_between(self.SCHOOL_TERMS[term_of_the_lesson][0],self.SCHOOL_TERMS[term_of_the_lesson][1]), datetime.min.time()))
        term_end_date = self.SCHOOL_TERMS[term_of_the_lesson][1]
        days_between_date_and_end_of_term = (term_end_date-_date.date()).days
        max_number_of_lessons = days_between_date_and_end_of_term//_interval_between_lessons[0]
        _number_of_lessons = 1
        if max_number_of_lessons>=2:
            _number_of_lessons = randint(1,max_number_of_lessons-1)
        request = Request.objects.create(
                    user=user,
                    number_of_lessons=_number_of_lessons,
                    interval_between_lessons=_interval_between_lessons[0],
                    relation_id= relation_id,
                    duration_of_lessons=self.LESSON_DURATIONS[randint(0,len(self.LESSON_DURATIONS)-1)],
                    fulfilled=is_fulfilled,
                    further_information='Lorem ipsum.',
                    date=_date
                    )
        request.availability.set(sample(self.DAYS_OF_THE_WEEK_INSTANCES, randint(1,len(self.DAYS_OF_THE_WEEK_INSTANCES)-1)))
        return request
    

    def _create_fulfilled_and_paid_request_for_john_doe(self):
        john_doe_user =  User.objects.get(email='john.doe@example.org')
        john_doe_request = self.create_random_request_for_user(john_doe_user,-1,True)
        john_doe_request.availability.set(sample(self.DAYS_OF_THE_WEEK_INSTANCES, randint(1,len(self.DAYS_OF_THE_WEEK_INSTANCES)-1)))
        invoice = self._create_booking_for_request_and_return_invoice(john_doe_request)
        self.pay_invoice(invoice)

    def create_child_for_user(self,user,child_first_name, child_last_name):
        return Child.objects.create(parent=user,first_name=child_first_name,last_name=child_last_name)

    def _create_booking_for_request_and_return_invoice(self,request):
        price_per_hour=randint(10,20)
        _invoice = self.create_invoice(request,price_per_hour)
        Booking.objects.create(
            invoice= _invoice,
            term_id= self.find_term_from_date(request.date),
            day_of_the_week= self.DAYS_OF_THE_WEEK_INSTANCES[randint(0,6)],
            time_of_the_day= f"{str(randint(0,11)).zfill(2)}:{str(randint(0,59)).zfill(2)}",
            user= request.user,
            relation_id= request.relation_id,
            teacher= self.faker.name(),
            start_date= request.date,
            end_date= request.date + timedelta(days=request.number_of_lessons*request.interval_between_lessons),
            duration_of_lessons= self.LESSON_DURATIONS[randint(0,len(self.LESSON_DURATIONS)-1)],
            interval_between_lessons=request.interval_between_lessons,
            number_of_lessons= request.number_of_lessons,
            further_information= request.further_information
        )
        return _invoice

    def pay_invoice(self,invoice):
        amount_paid = invoice.full_amount
        BankTransaction.objects.create(
            date = timezone.now(),
            student = invoice.student,
            amount = amount_paid,
            invoice = invoice
        )
        invoice.paid_amount = amount_paid
        invoice.fully_paid=True
   
    def overpay_invoice(self,invoice):
        amount_paid = invoice.full_amount + randint(5,100)
        BankTransaction.objects.create(
            date = timezone.now(),
            student = invoice.student,
            amount = amount_paid,
            invoice = invoice
        )
        invoice.paid_amount = amount_paid
        invoice.fully_paid=True

    def underpay_invoice(self,invoice):
        amount_paid = invoice.full_amount - randint(0,int(invoice.full_amount+1))
        BankTransaction.objects.create(
            date = timezone.now(),
            student = invoice.student,
            amount = amount_paid,
            invoice = invoice
        )
        invoice.paid_amount = amount_paid

    def create_invoice(self,request, hourly_cost):
        _student = Student.objects.get(user__email=request.user)
        invoice_number = self.generate_invoice_number(_student)

        #Calculate amount to pay
        total_required = (float(hourly_cost) * request.number_of_lessons * request.duration_of_lessons / 60)

        #Create invoice
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            student=_student,
            full_amount=total_required,
            paid_amount=0,
            fully_paid=False
        )
        invoice.full_clean()
        invoice.save()

        return invoice

    def generate_invoice_number(self,user):
        invoice_number = ""
        user_id = user.id
        number_of_invoices_for_user = Invoice.objects.all().filter(student=user).count() + 1
        for i in range(4-len(str(user_id))):
            invoice_number += "0"
        invoice_number = invoice_number + str(user_id) + "-"
        for i in range(3-len(str(number_of_invoices_for_user))):
            invoice_number += "0"
        invoice_number += str(number_of_invoices_for_user)
        return invoice_number
    
    def find_term_from_date(self,date): #Returns the term of the date
        term = SchoolTerm.objects.all().filter(end_date__gte=date).filter(start_date__lte=date).first()
        if not term:
            school_terms_starting_later = SchoolTerm.objects.filter(start_date__gte=date)
            min_start_date = school_terms_starting_later[0].start_date
            term = school_terms_starting_later[0]
            for term_in_list in school_terms_starting_later:
                if term.start_date < min_start_date:
                    min_start_date = term_in_list.start_date
                    term = term_in_list
        return term

    def database_is_empty(self):
        return SchoolTerm.objects.all().count() + DayOfTheWeek.objects.all().count() + Request.objects.all().count() + Student.objects.all().count() + Booking.objects.all().count() + BankTransaction.objects.all().count() + Invoice.objects.all().count() + Child.objects.all().count() == 0