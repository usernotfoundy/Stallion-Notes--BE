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
from .serializer import *
from authentication.models import *
from authentication.serializer import *
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
# from django.conf import settings
from authentication.views import TokenAuthentication
from purchase_management.models import *
from purchase_management.serializer import *
from book_management.models import *
from book_management.serializer import *
# from django.conf import settings
from django.http import Http404
import hashlib
from django.shortcuts import get_object_or_404

class ViewUsersAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):  # Modify get method to accept request
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True) 

        payload = []

        for user in serializer.data:
            # course_id = user['course'],  # Use get() to handle NoneType
            course = None
            college_abbr = None

            course_id = user['course']
            if course_id:
                course = Course.objects.get(id=course_id)
                course_abbr = course.course_abbr
                college_abbr = course.college.college_abbr
            else:
                course_abbr = "null"

            user_info = {
                'id': user['id'],
                'username': user['username'],
                'first_name': user['first_name'],
                'middle_name': user['middle_name'],
                'last_name': user['last_name'],
                'email': user['email'],
                'college': college_abbr,
                'course': course_abbr,
                'is_flag': user['is_flag'],
                'is_verified': user['is_verified'],
            }
            payload.append(user_info)

        return Response(payload, status=status.HTTP_200_OK)

class ViewTransaction(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PurchaseSerializer

    def get(self, request):
        queryset = Purchase_History.objects.all().order_by('-id')
        serializer = self.serializer_class(queryset, many=True)

        payload = []
        
        for purchase_data in serializer.data:
            # Assuming the serializer returns a dictionary representation of the Purchase_History object
            try:
                purchase = Purchase_History.objects.get(id=purchase_data['id'])
            except Purchase_History.DoesNotExist:
                # Handle the case where the Purchase_History object doesn't exist
                continue
            book = Book.objects.get(id=purchase_data['purchase_book'])
            if book.status_book == "pre-purchased":
                purchase_info = {
                    'id': purchase.id,
                    'user': purchase.user.username,
                    'seller': purchase.seller.username,
                    'purchase_book': book.title,
                    'book_id':book.id,
                    # 'purchase_book_id': book,
                    'created_at': purchase.created_at,
                    'transaction_hash': purchase.transaction_hash,
                    'claim_hub': purchase.purchase_book.user.course.college.college_abbr,
                }
                payload.append(purchase_info)

        return Response(payload, status=status.HTTP_200_OK)

class ApproveTransaction(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = BookSerializer
    # queryset = Purchase_History.objects.all()

    def update(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        print(book_id)

        try:
            # Get the book instance based on book_id
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

        book.status_book = "purchased"
        book.save()

        serialized_book = self.serializer_class(book).data

        return Response({'message': 'purchased book successfully', 'purchase': serialized_book}, status=status.HTTP_200_OK)

class DeclineTransaction(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        purchase_id = self.kwargs.get('pk')
        print(purchase_id)
        try:
            user_purchase = Purchase_History.objects.get(pk=purchase_id)
            return user_purchase
        except Purchase_History.DoesNotExist:
            raise Http404("Purchase does not exist")

    def update(self, request, *args, **kwargs):
        purchase = self.get_object()
        serializer = self.get_serializer(purchase, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update the related book status
            book = purchase.purchase_book
            book.status_book = "uploaded"
            book.save()
            return Response(serializer.data)
        return Response({'message':'uploaded book again', 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        purchase = self.get_object()
        # Update the related book status before deleting the purchase
        book = purchase.purchase_book
        book.status_book = "uploaded"
        book.save()
        purchase.delete()
        return Response("Purchase deleted successfully", status=status.HTTP_204_NO_CONTENT)

class DataStatisticsAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):  # Modify get method to accept request
        users_count = User.objects.count()
        books_count = Book.objects.count()
        pre_purchased = Book.objects.filter(status_book='pre-purchased').count()
        purchased = Book.objects.filter(status_book='purchased').count()

        payload = {
            'users_count': users_count,
            'books_count': books_count,
            'pre_purchased': pre_purchased,
            'purchased': purchased,
        }

        return Response(payload, status=status.HTTP_200_OK)
    
class CreateDonorAPIView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DonorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                user = self.request.user
                donor = self.request.data.get('name')
                book_id = self.request.data.get('book')
                print("user: ", user)
                print("donor: ", donor)

                # admin = get_object_or_404(User, pk=user)
                book = get_object_or_404(Book, pk=book_id)

                donor_data = Donor.objects.create(
                    name=donor,
                    admin=user,
                    book=book,
                )

                serialized_data = DonorSerializer(donor_data).data

                return Response(serialized_data, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({"error": "You're not logged-in."}, status=status.HTTP_200_OK)

class VerifyUserAPIView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        verification = request.data.get('is_verified')

        try:
            user = User.objects.get(id=user_id)
        
        except User.DoesNotExist:
            return Response({'message': 'user does not exists'}, status=status.HTTP_404_NOT_FOUND)
        
        if verification == True:
            user.is_verified = True
            user.save()
            serialized_user = self.serializer_class(user).data

            return Response({'message': 'User Approved Successfully', 'user': serialized_user}, status=status.HTTP_200_OK)
        else:
            user.is_flag = True
            user.save()
            serialized_user = self.serializer_class(user).data
            return Response({'message': 'User has been flagged as rejected', 'user': serialized_user}, status=status.HTTP_200_OK)

class ToVerifyUserAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        queryset = User.objects.all().order_by('-id')
        serializer = self.serializer_class(queryset, many=True)

        payload = []
        
        for user_data in serializer.data:
            # Assuming the serializer returns a dictionary representation of the Purchase_History object
            try:
                user = User.objects.get(id=user_data['id'])
            except User.DoesNotExist:
                # Handle the case where the Purchase_History object doesn't exist
                continue
            # book = Book.objects.get(id=purchase_data['purchase_book'])
            course = None
            college_abbr = None

            course_id = user_data['course']
            if course_id:
                course = Course.objects.get(id=course_id)
                course_abbr = course.course_abbr
                college_abbr = course.college.college_abbr
            else:
                course_abbr = "null"

            if user.is_verified == False and user.is_flag == False:
                user_info = {
                    'id': user.id,
                    'user': user.username,
                    'first_name': user.first_name,
                    'middle_name': user.middle_name,
                    'last_name': user.last_name,
                    'course_abbr': course_abbr,
                    'college_abbr': college_abbr
                }
                payload.append(user_info)

        return Response(payload, status=status.HTTP_200_OK)
    
class UpdateTargetUser(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]  # Specify authentication classes
    permission_classes = [permissions.IsAuthenticated]  # Require admin permissions
    serializer_class = UserSerializer  # Specify the serializer class to use for updating the user

    def get_object(self):
        # Get the username from the request data
        username = self.request.data.get('username')
        print(username)
        if not username:
            raise Http404("Username is required.")
        
        # Retrieve the user instance based on the username
        user = User.objects.get(username=username)
        return user

    def update(self, request, *args, **kwargs):
        # Determine if the update should be partial or full
        partial = kwargs.pop('partial', False)
        
        # Get the user instance to update
        instance = self.get_object()
        
        # Create a serializer instance with the user instance and request data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        # Validate the serializer data
        serializer.is_valid(raise_exception=True)
        
        # Perform the update
        self.perform_update(serializer)

        # Update the user's password if provided in the request
        new_password = request.data.get('password')
        if new_password:
            instance.set_password(new_password)
            instance.save()
        
        # Return the payload in the response with status 200 OK
        return Response({'message': 'Password updated successfully!'}, status=status.HTTP_200_OK)