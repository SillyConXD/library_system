from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from .models import Book, Loan, Reservation, Author, Genre, Publisher
from .forms import UserRegisterForm, BookForm, LoanForm, ReservationForm
from django.utils import timezone
from .filters import BookFilter
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.shortcuts import render
from .models import Reservation


@login_required
@user_passes_test(lambda u: u.is_librarian or u.is_admin)
def fulfill_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if not reservation.fulfilled:
        reservation.fulfilled = True
        reservation.save()
        # Можно сразу создать Loan для этого пользователя и книги
        Loan.objects.create(
            book=reservation.book,
            borrower=reservation.user,
            loan_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(weeks=4)
        )
        messages.success(request, 'Бронирование отмечено как выданное и книга выдана читателю!')
    else:
        messages.info(request, 'Это бронирование уже выполнено.')
    return redirect('reservation-list')
def home(request):
    num_books = Book.objects.count()
    num_available = Book.objects.filter(available__gt=0).count()
    num_loans = Loan.objects.filter(returned_date__isnull=True).count()
    return render(request, 'catalog/home.html', {
        'num_books': num_books,
        'num_available': num_available,
        'num_loans': num_loans,
    })

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'catalog/register.html', {'form': form})

class BookListView(ListView):
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter = BookFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        user = self.request.user
        # Кнопка "Reserve" доступна только читателю, если книга доступна и нет активной брони на эту книгу
        can_reserve = (
            user.is_authenticated and
            getattr(user, 'is_reader', False) and
            book.available > 0 and
            not book.reservations.filter(user=user, fulfilled=False, expiry_date__gt=timezone.now()).exists()
        )
        context['can_reserve'] = can_reserve
        return context

@login_required
def reserve_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.book = book
            reservation.save()
            messages.success(request, 'Книга успешно забронирована!')
            return redirect('my-reservations')
    else:
        form = ReservationForm()
    return render(request, 'catalog/reserve_book.html', {'form': form, 'book': book})

class LoanListView(ListView):
    model = Loan
    template_name = 'catalog/loan_list.html'
    context_object_name = 'loans'
    paginate_by = 10

@login_required
def loan_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.book = book
            loan.borrower = request.user
            loan.loan_date = timezone.now().date()
            loan.due_date = timezone.now().date() + timezone.timedelta(weeks=4)
            loan.save()
            messages.success(request, 'Книга успешно выдана!')
            return redirect('my-loans')
    else:
        form = LoanForm()
    return render(request, 'catalog/loan_book.html', {'form': form, 'book': book})

@login_required
def return_book(request, pk):
    loan = get_object_or_404(Loan, pk=pk, borrower=request.user)
    if request.method == 'POST':
        loan.returned_date = timezone.now().date()
        loan.save()
        messages.success(request, 'Книга успешно возвращена!')
        return redirect('my-loans')
    return render(request, 'catalog/return_book.html', {'loan': loan})

class UserLoansView(ListView):
    model = Loan
    template_name = 'catalog/user_loans.html'
    context_object_name = 'loans'
    paginate_by = 10

    def get_queryset(self):
        return Loan.objects.filter(borrower=self.request.user)

class UserReservationsView(ListView):
    model = Reservation
    template_name = 'catalog/user_reservations.html'
    context_object_name = 'reservations'
    paginate_by = 10

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

@login_required
def report_overdue_loans(request):
    overdue_loans = Loan.objects.filter(due_date__lt=timezone.now().date(), returned_date__isnull=True)
    return render(request, 'catalog/report_overdue.html', {'loans': overdue_loans})

@login_required
def report_popular_books(request):
    from django.db.models import Count
    popular_books = Book.objects.annotate(num_loans=Count('loans')).order_by('-num_loans')[:10]
    return render(request, 'catalog/report_popular.html', {'books': popular_books})

@login_required
@user_passes_test(lambda u: getattr(u, 'is_librarian', False) or getattr(u, 'is_admin', False))
def reservation_list(request):
    reservations = Reservation.objects.all().order_by('-reservation_date')
    return render(request, 'catalog/reservation_list.html', {'reservations': reservations, 'now': timezone.now()})

@login_required
@user_passes_test(lambda u: getattr(u, 'is_librarian', False) or getattr(u, 'is_admin', False))
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if not reservation.fulfilled:
        reservation.delete()
        messages.success(request, 'Бронирование отменено.')
    else:
        messages.info(request, 'Нельзя отменить уже выполненное бронирование.')
    return redirect('reservation-list')

@login_required
def profile(request):
    return render(request, 'catalog/profile.html', {'user_obj': request.user})