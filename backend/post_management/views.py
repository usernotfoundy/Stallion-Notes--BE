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
from django.shortcuts import get_object_or_404
# from authentication.serializer import MiscSerializer

class PostAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def list(self, request, *args, **kwargs):
        # Retrieve all book posts
        # book_posts = Book.objects.all()

        # Retrieve all book posts in reverse order
        book_posts = Book.objects.exclude(status_book='pre-purchased').order_by('-id')

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
                'subtitle': book_post.subtitle,
                'description':book_post.description,
                'price': book_post.price,
                'created_at': book_post.created_at,
                'book_img_url': book_img_url,
                'wishlist': book_post.wishlist,
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

class PostSearchAPIView(generics.ListAPIView):
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
    
class AddWishlistAPIView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer

    def get_object(self):
        book_id = self.request.data.get('book_id')
        book = Book.objects.get(pk=book_id)
        return book
    
    def update(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        action = request.data.get('action')  # Get the action from request data
        
        if action not in ['like', 'unlike']:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()

        if action == 'like':
            instance.wishlist += 1
        elif action == 'unlike':
            instance.wishlist -= 1
            if instance.wishlist < 0:
                instance.wishlist = 0

        instance.save()

        # Prepare response payload
        payload = {
            "message": f"Book '{instance.title}' wishlist count updated",
            "wishlist_count": instance.wishlist,
        }

        return Response(payload, status=status.HTTP_200_OK)
    
class CreateWishlistAPIView(generics.CreateAPIView):
    serializer_class = MyWishlistSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print("book: ", self.request.data.get('book'))

        if serializer.is_valid():
            try:
                book_id = request.data.get('book')

                user = self.request.user

                book = get_object_or_404(Book, pk=book_id)

                wishlist = MyWishlist.objects.create(
                    user=user,
                    book=book
                )
                serialized_data = MyWishlistSerializer(wishlist).data
                return Response(serialized_data, status=status.HTTP_201_CREATED)
            
            except Book.DoesNotExist:
                return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Serializer Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class WishlistAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    
    serializer_class = MyWishlistSerializer

    def list(self, request, *args, **kwargs):
        # Retrieve all book posts
        # book_posts = Book.objects.all()

        # Retrieve all book posts in reverse order
        user = self.request.user
        wishlist_items = MyWishlist.objects.filter(user=user).order_by('-id')

        # Initialize an empty list to store the payload
        payload = []
        for wishlist_item in wishlist_items:
            
             # Construct the URL for the book image
            book_img_url = None
            if wishlist_item.book.book_img:
                book_img_url = request.build_absolute_uri(wishlist_item.book.book_img.url)

            # Construct the URL for the user's image
            user_img_url = None
            if wishlist_item.book.user.profile_img:
                user_img_url = request.build_absolute_uri(wishlist_item.book.user.profile_img.url)

            post_data = {
                'id': wishlist_item.id,
                'book_id': wishlist_item.book.id,
                'title': wishlist_item.book.title,
                'subtitle': wishlist_item.book.subtitle,
                'description': wishlist_item.book.description,
                'price': wishlist_item.book.price,
                'created_at': wishlist_item.book.created_at,
                'book_img_url': book_img_url,
                'wishlist_count': wishlist_item.book.wishlist,
                'user': wishlist_item.book.user.username,
            }
            payload.append(post_data)

        return Response(payload, status=status.HTTP_200_OK)


class DeleteWishlistAPIView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = MyWishlistSerializer

    queryset = MyWishlist.objects.all()

    def get_object(self):
        # Extract the wishlist ID from the URL kwargs
        wishlist_id = self.kwargs.get('pk')
        try:
            # Retrieve the wishlist object based on the ID
            book = MyWishlist.objects.get(pk=wishlist_id)
            return book
        except Wishlist.DoesNotExist:
            # If the wishlist does not exist, raise a 404 Not Found exception
            raise Http404("wishlist does not exist")

    def delete(self, request, *args, **kwargs):
        # Retrieve the book object using the get_object method
        Wishlist = self.get_object()

        # Perform the deletion
        Wishlist.delete()

        # Return a success response
        return Response("wishlist removed successfully", status=status.HTTP_204_NO_CONTENT)
