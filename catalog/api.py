from rest_framework import viewsets, permissions
from rest_framework import serializers
from .models import Book, Author, Genre, Publisher, Loan, Reservation

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]