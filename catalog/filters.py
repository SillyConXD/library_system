import django_filters
from .models import *
from django.utils import timezone

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author__last_name = django_filters.CharFilter(lookup_expr='icontains')
    genre = django_filters.ModelMultipleChoiceFilter(
        field_name='genre__name',
        to_field_name='name',
        queryset=Genre.objects.all()
    )
    
    class Meta:
        model = Book
        fields = ['title', 'author__last_name', 'genre', 'status']

class LoanFilter(django_filters.FilterSet):
    book__title = django_filters.CharFilter(lookup_expr='icontains')
    borrower__username = django_filters.CharFilter(lookup_expr='icontains')
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')
    
    class Meta:
        model = Loan
        fields = ['book__title', 'borrower__username', 'is_overdue']
    
    def filter_overdue(self, queryset, name, value):
        if value:
            return queryset.filter(
                returned_date__isnull=True,
                due_date__lt=timezone.now().date()
            )
        return queryset