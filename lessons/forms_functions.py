from .models import Student, Invoice, SchoolTerm

def create_invoice(booking, hourly_cost):
    '''Creates invoice for the user contained in Booking with hourly cost hourly_cost'''

    user = Student.objects.get(user__email=booking.user)

    invoice_number = generate_invoice_number(user)

    # Calculate amount to pay
    total_required = (float(hourly_cost) * booking.number_of_lessons * booking.duration_of_lessons / 60)

    # Create invoice
    invoice = Invoice.objects.create(
        invoice_number=invoice_number,
        student=user,
        full_amount=total_required,
        paid_amount=0,
        fully_paid=False
    )
    invoice.full_clean()
    invoice.save()

    return invoice_number


def generate_invoice_number(user):
    '''Generates and returns a new unique invoice number for user'''
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


def find_term_from_date(date):
    '''Returns the term of the date'''
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