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
from authentication.models import *
from book_management.models import *
from book_management.serializer import *
from book_management.views import *
# from authentication.serializer import MiscSerializer

class PostAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def list(self, request, *args, **kwargs):
        # Retrieve all book posts
        book_posts = Book.objects.all()

        # Initialize an empty list to store the payload
        payload = []

        # Iterate over each book post
        for book_post in book_posts:
            # Construct the URL for the book image
            book_img_url = None
            if book_post.book_img:
                book_img_url = request.build_absolute_uri(book_post.book_img.url)

            # Construct the URL for the user's image
            user_img_url = None
            if book_post.user.profile_img:
                user_img_url = request.build_absolute_uri(book_post.user.profile_img.url)

            # Create a dictionary for the book post payload
            post_data = {
                'id': book_post.id,
                'title': book_post.title,
                'created_at': book_post.created_at,
                'book_img_url': book_img_url,
                'user': {
                    'username': book_post.user.username,
                    # 'email': book_post.user.email,
                    'profile_img_url': user_img_url,  # Include user's profile image URL
                    # Add other user-related fields as needed
                }
                # Add other book-related fields as needed
            }

            # Append the book post dictionary to the payload list
            payload.append(post_data)

        # Return the payload as a JSON response
        return Response(payload, status=status.HTTP_200_OK)
    
# class PostManagement(generics.ListAPIView):
#     authentication_classes = [TokenAuthentication]  
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = MiscSerializer

#     def get_queryset(self):
#         # Get the authenticated user
#         user = self.request.user
        
#         # Get the genre_pref field for the user from the Misc table
#         misc_object = Misc.objects.filter(user=user).first()
#         if misc_object:
#             genre_pref = misc_object.genre_pref
#             if genre_pref:
#                 # Split the genre_pref string by comma and store them in a list
#                 genre_list = genre_pref.split(',')
#                 return genre_list
        
#         # If no genre_pref is found for the user or it's empty, return an empty queryset
#         return []

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
        
