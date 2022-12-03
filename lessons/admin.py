from django.contrib import admin
from .models import User, Student, BankTransaction, Booking, Request, SchoolTerm, Invoice


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'last_name', 'is_active', 'id'
    ]

@admin.register(BankTransaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'student', 'amount', 'invoice'
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
        'relation_id',
        'number_of_lessons', 
        'interval_between_lessons', 
        'duration_of_lessons',
        'further_information',
        'fulfilled'
    ]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_id',
        #'day_of_the_week',
        'time_of_the_day',
        'user',
        'relation_id',
        'teacher',
        'start_date',
        'duration_of_lessons',
        'interval_between_lessons',
        'number_of_lessons',
        'further_information'
    ]

@admin.register(SchoolTerm)
class SchoolTermAdmin(admin.ModelAdmin):
    list_display = [
        'term_name',
        'start_date',
        'end_date'
    ]

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number',
        'student',
        'full_amount',
        'paid_amount'
    ]