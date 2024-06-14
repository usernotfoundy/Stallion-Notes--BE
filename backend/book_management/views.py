from rest_framework.authtoken.models import Token
from rest_framework import generics, permissions
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from .models import *
from authentication.models import *
from .serializer import *
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from authentication.views import TokenAuthentication
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from django.http import Http404

import re
from fuzzywuzzy import process

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import nltk
from django.db.models import Q

# Download NLTK resources if not already done
# nltk.download('punkt')

class StemmedTfidfVectorizer(TfidfVectorizer):
    def __init__(self, stemmer=None, **kwargs):
        super(StemmedTfidfVectorizer, self).__init__(**kwargs)
        self.stemmer = stemmer or PorterStemmer()

    def build_analyzer(self):
        analyzer = super(StemmedTfidfVectorizer, self).build_analyzer()
        return lambda doc: (self.stemmer.stem(w) for w in analyzer(doc))

class BookAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = BookSerializer

    def get_queryset(self):
        # Filter the queryset based on the authenticated user
        return Book.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        # Retrieve queryset for books associated with the authenticated user
        queryset = self.get_queryset()

        # Serialize the queryset
        serializer = self.serializer_class(queryset, many=True)

        # Extract book image URL for each book
        payload = []
        for book_data in serializer.data:
            book_img_url = None
            if book_data["book_img"]:
                book_img_url = request.build_absolute_uri(book_data["book_img"])

            #Genre is accessed in OrdereDict
            genre_dict = book_data['genre']
            if genre_dict:
                genre = genre_dict['genre_name']
            else:
                genre = "null"

            # Construct book info dictionary including the book image URL
            book_info = {
                'id': book_data['id'],
                'title': book_data['title'],
                'author': book_data['author'],
                'description': book_data['description'],
                'price': book_data['price'],
                'genre': genre,
                'img': book_img_url,
                # Add other fields as needed
            }
            payload.append(book_info)

        # Return the book details in the response payload
        return Response(payload, status=status.HTTP_200_OK)

class BookCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
    
        if serializer.is_valid():
            try:
                # Extract genre_id from request data
                genre_id = request.data.get('genre')

                # Get user from request (assuming authentication is setup)
                user = self.request.user

                # Create a new Book object
                book = Book.objects.create(
                    user=user,
                    title=request.data.get('title'),
                    subtitle=request.data.get('subtitle'),
                    # isbn=request.data.get('isbn'),
                    # publisher=request.data.get('publisher'),
                    description=request.data.get('description'),
                    # status_book=request.data.get('status_book'),
                    price=request.data.get('price'),
                    author=request.data.get('author'),
                    genre_id=genre_id,
                    book_img=request.data.get('book_img'),
                    # wishlist=request.data.get('wishlist')
                )

                # Serialize the created Book object
                serialized_data = BookSerializer(book).data

                # Return success response
                return Response(serialized_data, status=status.HTTP_201_CREATED)

            except Genre.DoesNotExist:
                return Response({"error": "Genre not found."}, status=status.HTTP_404_NOT_FOUND)

        # If serializer is not valid, return error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookSearchAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer

    def get_queryset(self):
        query = self.kwargs.get('query')
        if not query:
            return []

        # Use the stemmer with TF-IDF
        vectorizer = StemmedTfidfVectorizer(stop_words='english')

        books = Book.objects.exclude(status_book='pre-purchased').order_by('-id')
        book_descriptions = [
            f"{book.title} {book.subtitle if book.subtitle else ''} {book.genre.genre_name if book.genre else ''}"
            for book in books
        ]

        # Create the matrix of book descriptions
        X = vectorizer.fit_transform(book_descriptions)
        query_vec = vectorizer.transform([query])
        similarities = cosine_similarity(X, query_vec).flatten()

        # Filter books by similarity score
        books_with_scores = sorted(
            [(book, score) for book, score in zip(books, similarities)],
            key=lambda x: x[1],
            reverse=True
        )

        return [book for book, score in books_with_scores if score > 0.01]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized_data = []

        for book in queryset:
            serialized_book = self.serializer_class(book).data
            if 'book_img' in serialized_book and serialized_book['book_img']:
                book_img_url = request.build_absolute_uri(serialized_book['book_img'])
                serialized_book['book_img'] = book_img_url
            serialized_data.append(serialized_book)

        return Response(serialized_data, status=status.HTTP_200_OK)
    
class BookUpdateAPIView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def get_object(self):
        book_id = self.request.data.get('id')
        # print("this is my ID: ", book_id)
        book = Book.objects.get(pk=book_id)
        return book

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Extract updated fields from the serializer
        updated_data = serializer.validated_data

        book_img_url = None
        if updated_data.get("book_img"):
            book_img_url = request.build_absolute_uri(updated_data["book_img"])

        # Construct the payload with updated book information
        payload = {
            "message": "Book updated successfully",
            "book": {
                "id": updated_data.get('id'),
                "title": updated_data.get('title'),
                "subtitle": updated_data.get('subtitle'),
                "author": updated_data.get('author'),
                "description": updated_data.get('description'),
                "genre": updated_data.get('genre'),
                "book_img": book_img_url,
            }
        }

        return Response(payload, status=status.HTTP_200_OK)

class BookDeleteAPIView(generics.DestroyAPIView):
    serializer_class = BookSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()

    def get_object(self):
        # Extract the book ID from the URL kwargs
        book_id = self.kwargs.get('pk')
        try:
            # Retrieve the book object based on the ID
            book = Book.objects.get(pk=book_id)
            return book
        except Book.DoesNotExist:
            # If the book does not exist, raise a 404 Not Found exception
            raise Http404("Book does not exist")

    def delete(self, request, *args, **kwargs):
        # Retrieve the book object using the get_object method
        book = self.get_object()

        # Perform the deletion
        book.delete()

        # Return a success response
        return Response("Book deleted successfully", status=status.HTTP_204_NO_CONTENT)

class GetGenreAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    # queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get(self, request, *args, **kwargs):
        queryset = Genre.objects.all()
        serializer = self.serializer_class(queryset, many=True)

        payload = []

        for genre_data in serializer.data:
            genre_info = {
                'id': genre_data['id'],
                'genre_name': genre_data['genre_name'],
            }
            payload.append(genre_info)
        return Response(payload, status=status.HTTP_200_OK)

class GenreCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = GenreSerializer

class BookExploreAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        # Retrieve queryset for books associated with the authenticated user
        books = Book.objects.exclude(Q(status_book='pre-purchased') | Q(status_book='purchased')).order_by('-id')
        # books = Book.objects.all()

        # Serialize the queryset
        # serializer = self.serializer_class(book, many=True)

        # Extract book image URL for each book
        payload = []
        for book_data in books:
            book_img_url = None
            if book_data.book_img:
                book_img_url = request.build_absolute_uri(book_data.book_img.url)
            
            genre_name = None
            if book_data.genre:
                genre_name = book_data.genre.genre_name
            else:
                genre_name = "Null"

            # Construct book info dictionary including the book image URL
            book_info = {
                'id': book_data.id,
                'seller': book_data.user.username,
                'title': book_data.title,
                'author': book_data.author,
                'description': book_data.description,
                'price': book_data.price,
                'genre': genre_name,
                'book_img': book_img_url,
                # Add other fields as needed
            }
            payload.append(book_info)

        # Return the book details in the response payload
        return Response(payload, status=status.HTTP_200_OK)