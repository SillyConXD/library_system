import django_tables2 as tables
from .models import *

class BookTable(tables.Table):
    title = tables.Column(linkify=True)
    author = tables.Column(accessor='author.__str__')
    status = tables.Column()
    
    class Meta:
        model = Book
        template_name = "django_tables2/bootstrap4.html"
        fields = ('title', 'author', 'status', 'available')

class LoanTable(tables.Table):
    book = tables.Column(linkify=True)
    borrower = tables.Column(accessor='borrower.__str__')
    is_overdue = tables.BooleanColumn()
    
    class Meta:
        model = Loan
        template_name = "django_tables2/bootstrap4.html"
        fields = ('book', 'borrower', 'loan_date', 'due_date', 'returned_date', 'is_overdue')

class FineTable(tables.Table):
    loan = tables.Column(accessor='loan.__str__')
    
    class Meta:
        model = Fine
        template_name = "django_tables2/bootstrap4.html"
        fields = ('loan', 'amount', 'paid', 'issue_date', 'payment_date')

class ReservationTable(tables.Table):
    book = tables.Column(linkify=True)
    user = tables.Column(accessor='user.__str__')
    
    class Meta:
        model = Reservation
        template_name = "django_tables2/bootstrap4.html"
        fields = ('book', 'user', 'reservation_date', 'expiry_date', 'fulfilled')