from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime
from .user_manager import UserManager
from decimal import Decimal


class DayOfTheWeek(models.Model):
    class Day(models.TextChoices):
        MONDAY = 'Monday'
        TUESDAY = 'Tuesday'
        WEDNESDAY = 'Wednesday'
        THURSDAY = 'Thursday'
        FRIDAY = 'Friday'
        SATURDAY = 'Saturday'
        SUNDAY = 'Sunday'

    order = models.PositiveIntegerField(validators=[MaxValueValidator(6)])
    day = models.CharField(max_length=10, editable=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.day


class User(AbstractBaseUser,PermissionsMixin):
    first_name = models.CharField(max_length = 50, blank=False, unique = False)
    last_name = models.CharField(max_length = 50, blank=False, unique = False)
    email = models.EmailField(unique = True, blank = False)
    is_active = models.BooleanField(
        ('active'),
        default=True,
        help_text=(
            'Designates whether this user should be '
            'treated as active. Unselect this instead '
            'of deleting accounts.'
        ),
    )
    is_superuser = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=(
            'Designates whether the user can log into '
            'this admin site.'
        ),
    )
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=(
            'Designates whether the user can log into '
            'this admin site.'
        ),
    )
    date_joined = models.DateTimeField(
        ('date joined'),
        default=timezone.now,
    )

    def is_admin(self):
        return self.groups.exists() and self.groups.all()[0].name == "Admin"

    def is_student(self):
        return self.groups.exists() and self.groups.all()[0].name == "Student"
    
    def is_admin_or_director(self):
        return self.is_admin() or self.is_superuser

    def get_group(self):
        if self.is_superuser:
            return 'Director'
        elif self.is_student():
            return 'Student'
        elif self.is_admin():
            return 'Admin'

    def get_full_name(self):
        if self.first_name != "" and self.last_name != "":
            return f"{self.first_name}, {self.last_name}"
        else:
            return ""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='user_record', blank=False)
    balance = models.DecimalField(default=0,max_digits=6, decimal_places=2, blank=False)

    def save(self, *args, **kwargs):
        super(Student, self).save(*args, **kwargs)
        if (not self.user.groups.exists() or self.user.groups.all()[0].name != "Student"):
            student_group = Group.objects.get(name='Student')
            student_group.user_set.add(self.user)

class SchoolTerm(models.Model):
    term_name = models.CharField(unique=True, blank=False, max_length=18)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)

    class Meta:
        ordering = ['start_date']

    def clean(self):
        # Clean is not invoked when you use save? I think?
        # Only on create()?? and is_valid()

        # Check valid dates
        if not(self.start_date and self.end_date):
            raise ValidationError("Date(s) are not in form YYYY-MM-DD")

        # Error if the start date is less than the end date
        if not(self.start_date < self.end_date):
            raise ValidationError("Start date must be before end date")

        current_school_terms = SchoolTerm.objects.exclude(term_name=self.term_name)

        # Check if the new term does not overlap any existing terms.
        for term in current_school_terms:
            # Check if the new date is valid, compares to see if the new start date falls between one of the
            # existing ranges, or if one of the existing start dates falls between the new range.
            if (term.start_date <= self.start_date < term.end_date) or (self.start_date <= term.start_date < self.end_date):
                raise ValidationError("There is a overlap with this new date range and ranges for existing terms")

    # If we want to override a school term even if a term with the same name already exists.
    # def save(self, *args, **kwargs):
    #     existing_term = SchoolTerm.objects.filter(term_name=self.term_name).exists()
    #     if existing_term:
    #         existing_term.delete()
    #     super().save()
class Child(models.Model):
    parent = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)


class Invoice(models.Model):

    def clean(self, *args, **kwargs):

        if self.paid_amount < 0:
            raise ValidationError('Paid amount cannot be lower than 0')

        if self.full_amount < 0:
            raise ValidationError('Paid amount cannot be lower than 0')

        if self.paid_amount > self.full_amount:
            raise ValidationError('Paid amount is greater than full amount')

        if self.paid_amount == self.full_amount and not self.fully_paid:
            raise ValidationError('Fully paid not marked as true despite invoice being fully paid')

        if self.paid_amount != self.full_amount and self.fully_paid:
            raise ValidationError('Fully paid marked as true but paid amount != full amount')

    invoice_number = models.CharField(
        unique=True,
        primary_key=True,
        max_length=8,
        blank=False,
        validators=[RegexValidator(
            regex=r'^\d{4}-\d{3}$',
            message='Invoice number must follow the format xxxx-yyy where x is the student number and y is the invoice number.'
        )]
    )
    student = models.ForeignKey(Student, blank=False, on_delete=models.CASCADE)
    full_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=False)
    paid_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default='0.00')
    fully_paid = models.BooleanField(default=False, blank=False)


class Request(models.Model):
    class IntervalBetweenLessons(models.IntegerChoices):
        ONE_WEEK = 7, '1 Week'
        TWO_WEEKS = 14, '2 Weeks'

    class LessonDuration(models.IntegerChoices):
        THIRTY_MINUTES = 30, '30 Minutes'
        FOURTY_FIVE_MINUTES = 45, '45 Minutes'
        SIXTY_MINUTES = 60, '60 Minutes'
    
    date = models.DateTimeField(
        blank=False,
        default=timezone.now,
        validators=[
            MaxValueValidator(
            limit_value=timezone.now,
            message="The request date can't be in the future.")]
    )
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    relation_id = models.IntegerField(MinValueValidator(-1))
    availability = models.ManyToManyField(DayOfTheWeek, blank=False)
    number_of_lessons = models.PositiveIntegerField(blank=False, default=1, 
                                                    validators=[MinValueValidator(1), MaxValueValidator(1000)])
    interval_between_lessons = models.PositiveIntegerField(choices=IntervalBetweenLessons.choices)
    duration_of_lessons = models.PositiveIntegerField(choices=LessonDuration.choices)
    further_information = models.CharField(blank=False, max_length=500)
    fulfilled = models.BooleanField(blank=False, default=False)


class Booking(models.Model):
    class IntervalBetweenLessons(models.IntegerChoices):
        ONE_WEEK = 7, '1 Week'
        TWO_WEEKS = 14, '2 Weeks'

    class LessonDuration(models.IntegerChoices):
        THIRTY_MINUTES = 30, '30 Minutes'
        FORTY_FIVE_MINUTES = 45, '45 Minutes'
        SIXTY_MINUTES = 60, '60 Minutes'

    invoice = models.OneToOneField(Invoice, blank=False, on_delete=models.CASCADE, unique=True)
    term_id = models.ForeignKey(SchoolTerm, blank=False, on_delete=models.CASCADE)
    day_of_the_week = models.ForeignKey(DayOfTheWeek, blank=True, on_delete=models.CASCADE)
    time_of_the_day = models.TimeField(auto_now=False, auto_now_add=False)
    user = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    relation_id = models.IntegerField(MinValueValidator(-1))
    teacher = models.CharField(blank=False, max_length=100)
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    duration_of_lessons = models.PositiveIntegerField(blank=False, choices=LessonDuration.choices)
    interval_between_lessons = models.PositiveIntegerField(choices=IntervalBetweenLessons.choices, blank=False)
    number_of_lessons = models.PositiveIntegerField(blank=False, validators=[MinValueValidator(1)])
    further_information = models.CharField(blank=False, max_length=500)




class BankTransaction(models.Model):
    date = models.DateField(
        blank=False,
        validators=[MaxValueValidator(
            limit_value=date.today,
            message='')]
    )
    student = models.ForeignKey(Student, blank=False, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=False)
    invoice = models.ForeignKey(Invoice, blank=False, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(BankTransaction, self).save(*args, **kwargs)
        self.invoice.paid_amount = Decimal(self.invoice.paid_amount) + Decimal(self.amount)
        overpay = Decimal(self.invoice.paid_amount) - Decimal(self.invoice.full_amount)

        if overpay >= 0:
            self.invoice.fully_paid = True
            self.invoice.paid_amount = self.invoice.full_amount
            self.student.balance = Decimal(self.student.balance) + overpay
            self.invoice.save()
            self.student.save()
            return
        self.invoice.save()



