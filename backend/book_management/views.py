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

        # Extract only required information about each book
        payload = []
        for book_data in serializer.data:
            book_info = {
                'title': book_data['title'],
                'author': book_data['author'],
                'description': book_data['description'],
                'genre': book_data['genre'],
                # Add other fields as needed
            }
            payload.append(book_info)

        # Return the book details in the response payload
        return Response(payload, status=status.HTTP_200_OK)
                
class BookCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = BookSerializer

    def perform_create(self, serializer):
        # Set the user field of the book instance to the logged-in user
        serializer.save(user=self.request.user)

class BookSearchAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer

    def get_queryset(self):
        query = self.request.data.get('query', '')  # Get the query from the request data
        books = Book.objects.all()

        # Vectorize book titles, subtitles, and genres
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform([f"{book.title} {book.subtitle} {book.genre.genre_name}" for book in books])
        query_vec = vectorizer.transform([query])

        # Calculate cosine similarity between query vector and book vectors
        similarities = cosine_similarity(X, query_vec)

        # Sort books by similarity score
        books_with_scores = list(zip(books, similarities))
        sorted_books = sorted(books_with_scores, key=lambda x: x[1], reverse=True)

        # Return list of books sorted by score
        return sorted_books

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Extract Book objects and scores from tuples in the queryset
        books_with_scores = [{'book': book[0], 'score': book[1][0]} for book in queryset]
        
        # Serialize book data along with genre and score
        serialized_data = []
        for item in books_with_scores:
            book = item['book']
            score = item['score']
            serialized_book = self.serializer_class(book).data
            serialized_book['score'] = score
            serialized_book['genre'] = book.genre.genre_name
            serialized_data.append(serialized_book)

        return Response(serialized_data, status=status.HTTP_200_OK)

class GetGenreAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    