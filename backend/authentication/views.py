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
from django.conf import settings


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the request
        authorization_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = authorization_header.split(' ')[1] if authorization_header.startswith('Bearer ') else None

        if token:
            # Authenticate the user using the token
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                return (user, None)
            except Token.DoesNotExist:
                raise AuthenticationFailed('Invalid token', code=status.HTTP_401_UNAUTHORIZED)
        else:
            return None

class ViewUsersAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class LoginAPIView(ObtainAuthToken):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        if user.is_authenticated:

            # Get or create a token for the authenticated user
            token, create = Token.objects.get_or_create(user=user)

            # Construct the response payload
            payload = {
                'message': 'Login successful',
                'user_info': {
                    'username': user.username,
                    'first name': user.first_name,
                    'middle name': user.middle_name,
                    'last name': user.last_name,
                },
                'token': token.key,
            }

            # Return a JSON response with the payload
            return Response(payload, status=status.HTTP_200_OK)
        else:
            # If authentication fails, return an error response
            payload = {
                'status': 'error',
                'message': 'Authentication failed',
            }
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)
    
class ViewProfileAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        # Retrieve the authenticated user
        user = self.request.user
        # Return a queryset containing only the authenticated user
        return User.objects.filter(pk=user.pk)

    def get(self, request, *args, **kwargs):
        # Retrieve the queryset containing the authenticated user
        queryset = self.get_queryset()
        # Serialize the user instance
        serializer = self.serializer_class(queryset, many=True)
        # Return the serialized user

        user_data = serializer.data[0]
        profile_img_url = None
        if user_data["profile_img"]:
            profile_img_url = request.build_absolute_uri(user_data["profile_img"])

        payload = {
            "username": user_data["username"],
            "first_name": user_data["first_name"],
            "middle_name": user_data["middle_name"],
            "last_name": user_data["last_name"],
            "email": user_data["email"],
            "profile_img": profile_img_url,
            "phone_number": user_data["phone_number"],
        }
        return Response(payload, status=status.HTTP_200_OK)
    
class UpdateUserAPIView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]  # Specify authentication classes
    permission_classes = [permissions.IsAuthenticated]  # Specify permission classes
    serializer_class = UserSerializer  # Specify the serializer class to use for updating the user

    def get_object(self):
        # Get the authenticated user from the request
        user = self.request.user
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

        # Retrieve the updated user instance
        updated_user = self.get_object()
        
        profile_img_url = None
        if updated_user.profile_img:
            profile_img_url = request.build_absolute_uri(updated_user.profile_img)

        # Construct the payload with updated user attributes
        payload = {
            "first_name": updated_user.first_name,  # Get the updated first name
            "middle_name": updated_user.middle_name,  # Get the updated middle name
            "last_name": updated_user.last_name,  # Get the updated last name
            "email": updated_user.email,  # Get the updated email
            "profile_img": profile_img_url,
            # "College": updated_user.course.college.college_name,  # Get the college name associated with the user's course
            # "Course": updated_user.course.course_name  # Get the course name associated with the user
        }
        
        # Return the payload in the response with status 200 OK
        return Response(payload, status=status.HTTP_200_OK)

class CollegeCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = CollegeSerializer

class CourseCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = CourseSerializer

class CollegeView(generics.ListAPIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    serializer_class = CollegeSerializer
    queryset = College.objects.all()

    
class CourseView(generics.ListAPIView):
    # authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    serializer_class = CourseSerializer

    def get_queryset(self):
        college_id = self.request.query_params.get('college')
        # print(college_id)
        if college_id:
            return Course.objects.filter(college_id=college_id)
        else:
            return Course.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True) 
        payload = []
        for course_data in serializer.data:
            college_id = course_data['college'] 
            college = College.objects.get(id=college_id)
            course_info = {
                'id': course_data['id'],
                'College': college.college_name,
                'Course': course_data['course_name'],
                'Abbrevation': course_data['course_abbr']
            }
            payload.append(course_info)

        # print(payload)

        return Response(payload, status=status.HTTP_200_OK)
