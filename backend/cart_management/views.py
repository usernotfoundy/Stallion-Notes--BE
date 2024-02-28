# from django.shortcuts import render
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
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from authentication.views import TokenAuthentication

# Create your views here.
class AddCartAPIView(generics.CreateAPIView):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = CartSerializer

class CartViewAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = CartSerializer

    def get_queryset(self):
        # Filter the queryset based on the authenticated user
        return Cart.objects.filter(user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)

        print(serializer.data)
        
        # Extract required information about each book and its seller
        payload = []
        for cart_data in serializer.data:
            book_id = cart_data['book']  # Assuming 'book' is an integer representing the book's ID
            book = Book.objects.get(id=book_id)  # Retrieve the Book object using the ID
            book_info = {
                'Current User': request.user.username,
                'Book Title': book.title,  # Access the title attribute of the Book object
                'Seller': book.user.username,  # Access the username of the user associated with the Book
            }
            payload.append(book_info)

        return Response(payload, status=status.HTTP_200_OK)