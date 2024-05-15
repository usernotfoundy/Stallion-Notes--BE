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
from book_management.serializer import BookSerializer
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from authentication.views import TokenAuthentication
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from django.http import Http404
import hashlib
from django.shortcuts import get_object_or_404

class PurchaseCreateAPIView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PurchaseSerializer

    def create(self, request, *args, **kwargs):
        # print("Request Data:", request.data)  # Debug: Print request data
        serializer = self.get_serializer(data=request.data)
    
        if serializer.is_valid():
            try:
            # Extract purchase_book and seller IDs
                purchase_book_id = request.data.get('purchase_book')
                seller_id = request.data.get('seller')

            # Get user from request (assuming authentication is setup)
                user = self.request.user

            # Retrieve book and seller objects
                purchase_book = get_object_or_404(Book, pk=purchase_book_id)
                seller = get_object_or_404(User, pk=seller_id)

            # Construct transaction_hash
                transaction_hash_str = f"{user}-{purchase_book}-{seller}-{timezone.now()}"
                transaction_hash = hashlib.sha256(transaction_hash_str.encode()).hexdigest()

            # Create a new Purchase_History object
                purchase_history = Purchase_History.objects.create(
                    user=user,
                    seller=seller,
                    purchase_book=purchase_book,
                    transaction_hash=transaction_hash,
                )

            # Serialize the created Purchase_History object
                serialized_data = PurchaseSerializer(purchase_history).data

            # Return success response
                return Response(serialized_data, status=status.HTTP_201_CREATED)

            except Book.DoesNotExist:
                return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

            except User.DoesNotExist:
                return Response({"error": "Seller not found."}, status=status.HTTP_404_NOT_FOUND)


class UpdatePurchasedBookAPIView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Book.objects.all()
    serializer_class = BookSerializer  # Use the serializer class for Book model

    def update(self, request, *args, **kwargs):
        # Get the book_id from the request
        book_id = request.data.get('book_id')

        # Validate if book_id exists
        if not book_id:
            return Response({'message': 'Book ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get the book instance based on book_id
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update the status_book field
        book.status_book = "pre-purchased"
        book.save()

        # Serialize the updated book instance
        serialized_book = self.serializer_class(book).data

        # Return success response with the updated book data
        return Response({'message': 'Book status updated successfully', 'book': serialized_book}, status=status.HTTP_200_OK)


class PurchaseListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        return Purchase_History.objects.filter(user=self.request.user).order_by('-id')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().select_related('seller', 'purchase_book')  # Optimize the query

        payload = []

        for purchase_history in queryset:
            purchase = {
                'id': purchase_history.id,
                'seller': purchase_history.seller.username,  # Get the seller's username
                'purchase_book': purchase_history.purchase_book.title,  # Get the book's title
                'created_at': purchase_history.created_at,  # Ensure the field name matches the model field
                'transaction_hash': purchase_history.transaction_hash,
            }
            payload.append(purchase)

        return Response(payload, status=status.HTTP_200_OK)