"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from authentication.views import *
from book_management.views import *
from cart_management.views import *

# for handling static files
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication APIs
    path('view-users/', ViewUsersAPIView.as_view(), name='view-user'),
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('update-user/', UpdateUserAPIView.as_view(), name='update-user'),
    path('view-profile/', ViewProfileAPIView.as_view(), name='view-profile'),

    # College & Course APIs
    path('create-college/', CollegeCreateView.as_view(), name='create-college'),
    path('view-college/', CollegeView.as_view(), name='view-college'),
    path('create-course/', CourseCreateView.as_view(), name='create-course'),
    path('view-course/', CourseView.as_view(), name='view-course'),

    # Book Management APIs
    path('view-books/', BookAPIView.as_view(), name='view-books'),
    path('create-book/', BookCreateView.as_view(), name='create-book'),
    path('update-book/', BookUpdateAPIView.as_view(), name='update-book'),
    path('delete-book/', BookDeleteAPIView.as_view(), name='delete-book'),
    path('search-book/', BookSearchAPIView.as_view(), name='search-book'),
    path('get-genre/', GetGenreAPIView.as_view(), name='get-genre'),

    # Cart Management APIs
    path('add-cart/', AddCartAPIView.as_view(), name='add-cart'),
    path('view-cart/', CartViewAPIView.as_view(), name='view-cart'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)