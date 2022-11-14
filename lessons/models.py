from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from datetime import date
from .user_manager import UserManager
from django.contrib.auth.models import PermissionsMixin

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
    balance = models.IntegerField(default=0)
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

class Request(models.Model):
    class IntervalBetweenLessons(models.IntegerChoices):
        ONE_WEEK = 1, '1 Week'
        TWO_WEEKS = 2, '2 Weeks'

    class LessonDuration(models.IntegerChoices):
        THIRTY_MINUTES = 30, '30 Minutes'
        FOURTY_FIVE_MINUTES = 45, '45 Minutes'
        SIXTY_MINUTES = 60, '60 Minutes'
    
    date = models.DateTimeField(
        blank=False,
        unique=True,
        validators=[MaxValueValidator(
            limit_value=timezone.now,
            message='')]
        )
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    availability = models.ManyToManyField(DayOfTheWeek, blank=False)
    number_of_lessons = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    interval_between_lessons = models.PositiveIntegerField(choices=IntervalBetweenLessons.choices)
    duration_of_lessons = models.PositiveIntegerField(choices=LessonDuration.choices)
    further_information = models.CharField(blank=False, max_length=500)
    fulfilled = models.BooleanField(blank=False, default=False)

class Booking(models.Model):
    class IntervalBetweenLessons(models.IntegerChoices):
        ONE_WEEK = 1, '1 Week'
        TWO_WEEKS = 2, '2 Weeks'

    class LessonDuration(models.IntegerChoices):
        THIRTY_MINUTES = 30, '30 Minutes'
        FORTY_FIVE_MINUTES = 45, '45 Minutes'
        SIXTY_MINUTES = 60, '60 Minutes'

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'
        SATURDAY = 6, 'Saturday'
        SUNDAY = 7, 'Sunday'

    invoice_id = models.CharField(max_length=8,
        unique=True,
        blank=False,
        validators=[RegexValidator(
            regex=r'^\d{4}-\d{3}$',
            message='Invoice number must follow the format xxxx-yyy where x is the student number and y is the invoice number.'
        )]
    )
    day_of_the_week = models.PositiveIntegerField(blank=False, choices=DayOfWeek.choices)
    time_of_the_day = models.TimeField(auto_now=False, auto_now_add=False)
    student = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)  # The same as user in Request model
    teacher = models.CharField(blank=False, max_length=100)
    start_date = models.DateField(blank=False)
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
    student = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=False)
    invoice_number = models.CharField(
        max_length=8,
        unique=True,
        blank=False,
        validators=[RegexValidator(
            regex=r'^\d{4}-\d{3}$',
            message='Invoice number must follow the format xxxx-yyy where x is the student number and y is the invoice number.'
        )]
    )
