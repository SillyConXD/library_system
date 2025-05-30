from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),

    # Book URLs
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('book/<int:pk>/reserve/', views.reserve_book, name='reserve-book'),

    # Loan URLs
    path('loans/', views.LoanListView.as_view(), name='loan-list'),
    path('book/<int:pk>/loan/', views.loan_book, name='loan-book'),
    path('loan/<int:pk>/return/', views.return_book, name='return-book'),

    # User URLs
    path('my-loans/', views.UserLoansView.as_view(), name='my-loans'),
    path('my-reservations/', views.UserReservationsView.as_view(), name='my-reservations'),

    # Report URLs
    path('reports/overdue/', views.report_overdue_loans, name='report-overdue'),
    path('reports/popular/', views.report_popular_books, name='report-popular'),

    # Registration URL
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    #Reservations
    path('reservations/', views.reservation_list, name='reservation-list'),
    path('reservation/<int:reservation_id>/fulfill/', views.fulfill_reservation, name='fulfill-reservation'),
    path('reservation/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel-reservation'),
    #Profile
    path('profile/', views.profile, name='profile'),

]