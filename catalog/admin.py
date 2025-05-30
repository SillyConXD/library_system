from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.contrib import admin
from .models import User, Author, Genre, Publisher, Book, Loan, Fine, Reservation

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre', 'status', 'available')
    list_filter = ('status', 'genre')
    search_fields = ('title', 'author__last_name', 'isbn')
    
    def display_genre(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])
    display_genre.short_description = 'Genre'

class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower', 'loan_date', 'due_date', 'returned_date', 'is_overdue')
    list_filter = ('returned_date', 'due_date')
    search_fields = ('book__title', 'borrower__username')
    
    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_reader', 'is_librarian')
    list_filter = ('is_reader', 'is_librarian')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_reader', 'is_librarian'),
        }),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(Book, BookAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Fine)
admin.site.register(Reservation)