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
from book_management.models import *
from .serializer import *
from book_management.serializer import *
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from authentication.views import TokenAuthentication
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RatingCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def perform_create(self, serializer):
        rating = serializer.validated_data.get('rating', 5)  # Default rating is set to 5
        # if rating < 3:
        #     rating = 3  # Minimum rating is set to 3
        serializer.save(rating=rating)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Customize the response payload
        response_data = {
            'message': 'Rating created successfully',
            'data': serializer.data
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

class RatingAPIView(generics.ListAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        ratings = self.get_queryset()

        # Initialize an empty list to store the payload
        payload = []

        # Iterate over each rating
        for rating in ratings:
            # Construct the payload for each rating
            rating_data = {
                'id': rating.id,
                'user': rating.user.username,
                'ratings': rating.rating,
                'comment': rating.comment,
                'created_at': rating.created_at,
            }
            payload.append(rating_data)

        # Return the payload as a JSON response
        return Response(payload, status=status.HTTP_200_OK)
    
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