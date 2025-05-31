from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Book, Author, Genre, Loan, Reservation
from django.utils import timezone
from django.db import IntegrityError

class BackendTests(TestCase):
    def setUp(self):
        # Создание тестовых пользователя, автора, жанра и книги
        self.user = User.objects.create_user(username='reader', password='pass', is_reader=True)
        self.librarian = User.objects.create_user(username='librarian', password='pass', is_librarian=True)
        self.author = Author.objects.create(first_name='Leo', last_name='Tolstoy')
        self.genre = Genre.objects.create(name='Роман')
        self.book = Book.objects.create(
            title='Война и мир',
            author=self.author,
            summary='...',
            isbn='1111111111111',
            quantity=2,
            available=2,
        )
        self.book.genre.add(self.genre)

    def test_create_loan_and_overdue(self):
        # Проверяет, что метод is_overdue() корректно определяет просроченный займ
        loan = Loan.objects.create(
            book=self.book,
            borrower=self.user,
            loan_date=timezone.now().date() - timezone.timedelta(days=30),
            due_date=timezone.now().date() - timezone.timedelta(days=1)
        )
        self.assertTrue(loan.is_overdue())

    def test_reservation_unique(self):
        # Проверяет, что нельзя создать дубликат бронирования для одной книги и пользователя
        Reservation.objects.create(book=self.book, user=self.user, expiry_date=timezone.now() + timezone.timedelta(days=7))
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(book=self.book, user=self.user, expiry_date=timezone.now() + timezone.timedelta(days=7))

    def test_book_availability_update(self):
        # Проверяет, что количество доступных книг уменьшается при выдаче и увеличивается при возврате
        loan = Loan.objects.create(
            book=self.book,
            borrower=self.user,
            loan_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=7)
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.available, 1)
        loan.returned_date = timezone.now().date()
        loan.save()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available, 2)

    def test_create_author(self):
        # Проверяет создание автора и корректность строкового представления
        author = Author.objects.create(first_name='Fyodor', last_name='Dostoevsky')
        self.assertEqual(str(author), 'Fyodor Dostoevsky')

    def test_create_genre(self):
        # Проверяет создание жанра и корректность строкового представления
        genre = Genre.objects.create(name='Детектив')
        self.assertEqual(str(genre), 'Детектив')

    def test_book_str(self):
        # Проверяет строковое представление книги
        self.assertEqual(str(self.book), 'Война и мир')

    def test_loan_delete_updates_book(self):
        # Проверяет, что удаление займа возвращает книгу в доступные
        loan = Loan.objects.create(
            book=self.book,
            borrower=self.user,
            loan_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=7)
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.available, 1)
        loan.delete()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available, 2)

    def test_reservation_expiry(self):
        # Проверяет, что бронирование может быть просрочено
        reservation = Reservation.objects.create(
            book=self.book,
            user=self.user,
            expiry_date=timezone.now() - timezone.timedelta(days=1)
        )
        self.assertTrue(reservation.expiry_date < timezone.now())

class FrontendTests(TestCase):
    def setUp(self):
        # Создание тестовых пользователя, автора, жанра и книги
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass', is_reader=True)
        self.librarian = User.objects.create_user(username='lib', password='testpass', is_librarian=True)
        self.author = Author.objects.create(first_name='Ivan', last_name='Ivanov')
        self.genre = Genre.objects.create(name='Фантастика')
        self.book = Book.objects.create(
            title='Тестовая книга',
            author=self.author,
            summary='Описание',
            isbn='1234567890123',
            quantity=2,
            available=2,
        )
        self.book.genre.add(self.genre)

    def test_homepage_accessible(self):
        # Проверяет, что главная страница доступна и содержит приветственный текст
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to Library System")

    def test_book_list_page(self):
        # Проверяет, что страница списка книг доступна и содержит название книги
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Каталог книг")
        self.assertContains(response, self.book.title)

    def test_register_form_errors(self):
        # Проверяет, что при ошибках в форме регистрации выводятся соответствующие сообщения
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'not-an-email',
            'password1': '123',
            'password2': '456',
        })
        self.assertContains(response, "This field is required.")
        self.assertContains(response, "Enter a valid email address.")
        self.assertContains(response, "The two password fields didn’t match.")

    def test_login_page(self):
        # Проверяет, что страница входа доступна и содержит слово "Login"
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")

    def test_profile_requires_login(self):
        # Проверяет, что страница профиля требует авторизации (редирект на логин)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # редирект на логин

    def test_profile_page(self):
        # Проверяет, что страница профиля доступна для авторизованного пользователя
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Профиль пользователя")

    def test_book_detail_page(self):
        # Проверяет, что страница детального просмотра книги доступна и содержит название книги
        response = self.client.get(reverse('book-detail', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)

    def test_reservation_list_requires_librarian(self):
        # Проверяет, что список бронирований требует авторизации библиотекаря
        response = self.client.get(reverse('reservation-list'))
        self.assertEqual(response.status_code, 302)  # редирект на логин или отказ
        self.client.login(username='lib', password='testpass')
        response = self.client.get(reverse('reservation-list'))
        self.assertEqual(response.status_code, 200)