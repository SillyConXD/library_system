from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

class User(AbstractUser):
    is_reader = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    registration_date = models.DateField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        related_name="catalog_user_groups",
        blank=True,
        help_text=_('The groups this user belongs to.')
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="catalog_user_permissions",
        blank=True,
        help_text=_('Specific permissions for this user.')
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-registration_date']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Проверяем, что пользователь не имеет одновременно несколько ролей
        role_count = sum([self.is_reader, self.is_librarian, self.is_admin])
        if role_count > 1:
            raise ValidationError(_('User can have only one role.'))
        super().save(*args, **kwargs)

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        ordering = ['name']

    def __str__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)

    class Meta:
        verbose_name = _('publisher')
        verbose_name_plural = _('publishers')
        ordering = ['name']

    def __str__(self):
        return self.name

class Book(models.Model):
    STATUS_CHOICES = [
        ('a', 'Available'),
        ('o', 'On loan'),
        ('r', 'Reserved'),
        ('m', 'Maintenance'),
    ]

    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    summary = models.TextField()
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    genre = models.ManyToManyField(Genre, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    available = models.IntegerField(default=1)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='a')
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')
        ordering = ['title']
        permissions = [
            ('can_mark_returned', 'Set book as returned'),
        ]

    def __str__(self):
        return self.title

    def update_availability(self):
        loans_count = self.loans.filter(returned_date__isnull=True).count()
        self.available = self.quantity - loans_count
        if self.available > 0:
            self.status = 'a'
        else:
            self.status = 'o'
        self.save()

class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('loan')
        verbose_name_plural = _('loans')
        ordering = ['-loan_date']
        permissions = [
            ('can_mark_returned', 'Set loan as returned'),
        ]

    def __str__(self):
        return f"{self.book} loaned to {self.borrower}"

    def is_overdue(self):
        return self.due_date < timezone.now().date() and not self.returned_date

    def save(self, *args, **kwargs):
        if not self.pk and not self.due_date:
            self.due_date = timezone.now().date() + timezone.timedelta(weeks=4)
        super().save(*args, **kwargs)
        self.book.update_availability()

class Fine(models.Model):
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    paid = models.BooleanField(default=False)
    issue_date = models.DateField(auto_now_add=True)
    payment_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('fine')
        verbose_name_plural = _('fines')
        ordering = ['-issue_date']

    def __str__(self):
        return f"Fine for {self.loan}: ${self.amount}"

class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    reservation_date = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)
    expiry_date = models.DateTimeField()

    class Meta:
        verbose_name = _('reservation')
        verbose_name_plural = _('reservations')
        ordering = ['-reservation_date']
        unique_together = ['book', 'user']

    def __str__(self):
        return f"Reservation for {self.book} by {self.user}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expiry_date = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
        if self.fulfilled:
            self.book.status = 'o'
            self.book.save()