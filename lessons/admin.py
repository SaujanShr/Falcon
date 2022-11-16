from django.contrib import admin
from lessons.models import User, Student, BankTransaction, Booking, Request

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'last_name', 'is_active',
    ]

@admin.register(BankTransaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'student', 'amount', 'invoice_number'
    ]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'balance'
    ]

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = [
        'date', 
        'user', 
        'number_of_lessons', 
        'interval_between_lessons', 
        'duration_of_lessons',
        'further_information',
        'fulfilled'
    ]

@admin.register(Booking)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_id',
        'day_of_the_week',
        'time_of_the_day',
        'student',
        'teacher',
        'start_date',
        'duration_of_lessons',
        'interval_between_lessons',
        'number_of_lessons',
        'further_information'
    ]

"""class BankTransaction(models.Model):
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
    )"""
