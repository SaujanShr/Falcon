from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from datetime import date

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


class User(AbstractUser):
    # Add code here. I've added placeholder code in the meantime.
    pass

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