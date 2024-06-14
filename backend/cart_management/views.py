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
from django.http import Http404

class AddCartAPIView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        # Get the logged-in user
        user = self.request.user

        # Extract the book ID from the request data
        book_id = self.request.data.get('book')

        # Check if the book_id already exists in the user's cart
        if Cart.objects.filter(user=user, book_id=book_id).exists():
            return Response({"error": "This book is already in your cart."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Create the cart object with the extracted data
            serializer.save(user=user, book_id=book_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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

        # print(serializer.data)
        
        # Extract required information about each book and its seller
        payload = []
        for cart_data in serializer.data:

            book_id = cart_data['book']  # Assuming 'book' is an integer representing the book's ID
            book = Book.objects.get(id=book_id)  # Retrieve the Book object using the ID

            cart_img_url = None
            if book.book_img:
                cart_img_url = request.build_absolute_uri(book.book_img.url)

            book_info = {
                'id': cart_data['id'],
                'book_id': book.id,
                'book_title': book.title,  # Access the title attribute of the Book object
                'seller': book.user.username,  # Access the username of the user associated with the Book
                'seller_id': book.user.id,
                'price': book.price,
                'book_img': cart_img_url,
            }
            payload.append(book_info)

        # print(payload)

        return Response(payload, status=status.HTTP_200_OK)

class CartDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()

    def get_object(self):
        # Extract the book ID from the URL kwargs
        cart_id = self.kwargs.get('pk')
        try:
            # Retrieve the book object based on the ID
            cart = Cart.objects.get(pk=cart_id)
            return cart
        except Cart.DoesNotExist:
            # If the book does not exist, raise a 404 Not Found exception
            raise Http404("Cart does not exist")

    def delete(self, request, *args, **kwargs):
        # Retrieve the book object using the get_object method
        cart = self.get_object()

        # Perform the deletion
        cart.delete()

        # Return a success response
        return Response("cart item deleted successfully", status=status.HTTP_204_NO_CONTENT)