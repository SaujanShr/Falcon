from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import date
from django.utils import timezone
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
    # username = models.CharField(
    #     max_length=30,
    #     unique=True,
    #     validators=[RegexValidator(
    #         regex=r'^@\w{3,}$',
    #         message='Username must consist of @ followed by at least three alphanumericals'
    #     )]
    # )
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
    
    date = models.CharField(blank=False, unique=True, max_length=50)
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    availability = models.ManyToManyField(DayOfTheWeek, blank=False)
    number_of_lessons = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    interval_between_lessons = models.PositiveIntegerField(choices=IntervalBetweenLessons.choices)
    duration_of_lessons = models.PositiveIntegerField(choices=LessonDuration.choices)
    further_information = models.CharField(blank=False, max_length=500)
    fulfilled = models.BooleanField(blank=False, default=False)

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
