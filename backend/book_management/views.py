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

    def perform_create(self, serializer):
        # Set the user field of the book instance to the logged-in user
        serializer.save(user=self.request.user)     

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Get the created book instance
        created_book = serializer.instance
        genre_id = self.request.data.get('genre')
        genre = Genre.objects.get(id=genre_id)

        # Construct the payload with the created book ID and a success message
        payload = {
            "message": "Book created successfully",
            "genre": genre.genre_name,
            "id": created_book.id
        }

        return Response(payload, status=status.HTTP_201_CREATED)

class BookSearchAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer

    def get_queryset(self):
        query = self.kwargs.get('query')
        query_length = len(query)
        n = min(3, query_length)

        books = Book.objects.exclude(status_book='pre-purchased').order_by('-id')

        # Vectorize book titles, subtitles, and genres
        vectorizer = TfidfVectorizer(stop_words='english')

        # Construct book descriptions, handling genre_name when genre is None
        book_descriptions = []
        for book in books:
            title = book.title
            subtitle = book.subtitle
            if book.genre:
                genre_name = book.genre.genre_name
            else:
                genre_name = ""
            description = f"{title} {subtitle} {genre_name}"
            book_descriptions.append(description)

        # Fit-transform the vectorizer
        X = vectorizer.fit_transform(book_descriptions)
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

            # Build absolute URL for book_img if it exists
            if 'book_img' in serialized_book and serialized_book['book_img']:
                book_img_url = request.build_absolute_uri(serialized_book['book_img'])
                serialized_book['book_img'] = book_img_url

            # Append the serialized book data to the list
            serialized_data.append(serialized_book)

        # Return Response with the serialized data
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
        book = Book.objects.exclude(status_book='pre-purchased').order_by('-id')
        # books = Book.objects.all()

        # Serialize the queryset
        serializer = self.serializer_class(book, many=True)

        # Extract book image URL for each book
        payload = []
        for book_data in serializer.data:
            book_img_url = None
            if book_data["book_img"]:
                book_img_url = request.build_absolute_uri(book_data["book_img"])

            # Construct book info dictionary including the book image URL
            book_info = {
                'id': book_data['id'],
                'title': book_data['title'],
                'author': book_data['author'],
                'description': book_data['description'],
                'price': book_data['price'],
                'genre': book_data['genre'],
                'book_img': book_img_url,
                # Add other fields as needed
            }
            payload.append(book_info)

        # Return the book details in the response payload
        return Response(payload, status=status.HTTP_200_OK)