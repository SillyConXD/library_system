from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book, Loan, Fine, Reservation

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'address']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_reader = True  # Всегда делаем нового пользователя читателем
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address']

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'publish_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['borrower']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['borrower'].queryset = User.objects.filter(is_reader=True)

class FineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = ['paid', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['book', 'user']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_reader=True)