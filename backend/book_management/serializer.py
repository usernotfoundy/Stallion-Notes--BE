from rest_framework import serializers
from .models import *
from authentication.serializer import UserSerializer

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['first_name','middle_name','last_name']

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genre_name']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(required=False)
    genre = GenreSerializer(required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
         model = Book
         fields = ['id', 'user', 'title', 'subtitle', 'isbn', 'publisher', 'description',
                   'status_book', 'price', 'author', 'genre', 'book_img']
         extra_kwargs = {'author': {'allow_null': True, 'required': False},
                         'genre': {'allow_null': True, 'required': False},
                         'description': {'allow_null': True, 'required': False},
                         'status_book': {'allow_null': True, 'required': False},
                         'book_img': {'allow_null': True, 'required': False},
                         'isbn': {'allow_null': True, 'required': False},
                         'price': {'allow_null': True, 'required': False},
                         'publisher': {'allow_null': True, 'required': False}}