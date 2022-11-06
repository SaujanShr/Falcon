from django.db import models
from django.core.validators import MinLengthValidator

class DayOfTheWeek(models.Model):
    day = models.CharField(max_length=10, editable=False)

    class Meta:
        ordering = ['day']
    
    def __str__(self):
        return self.day


class Request(models.Model):
    class Day(models.TextChoices):
        MONDAY = 'Monday'
        TUESDAY = 'Tuesday'
        WEDNESDAY = 'Wednesday'
        THURSDAY = 'Thursday'
        FRIDAY = 'Friday'
        SATURDAY = 'Saturday'
        SUNDAY = 'Sunday'

    class IntervalBetweenLessons(models.IntegerChoices):
        ONE_WEEK = 1, '1 Week'
        TWO_WEEKS = 2, '2 Weeks'

    class LessonDuration(models.IntegerChoices):
        THIRTY_MINUTES = 30, '30 Minutes'
        FOURTY_FIVE_MINUTES = 45, '45 Minutes'
        SIXTY_MINUTES = 60, '60 Minutes'

    student_id = models.CharField(
            max_length = 4,
            validators=[MinLengthValidator(4)]
        )
    availability = models.ManyToManyField(DayOfTheWeek)
    number_of_lessons = models.PositiveIntegerField(choices=LessonDuration.choices)
    interval_between_lessons = models.PositiveIntegerField(choices=IntervalBetweenLessons.choices)
    duration_of_lessons = models.PositiveIntegerField(choices=LessonDuration.choices)
    further_information = models.CharField(max_length=500)