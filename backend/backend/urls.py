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
from django.urls import path
from authentication.views import *
from book_management.views import *
from cart_management.views import *
from post_management.views import *
from rating_management.views import *
from purchase_management.views import *
from admin_management.views import *

# for handling static files
# from django.conf import Settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication APIs
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('update-user/', UpdateUserAPIView.as_view(), name='update-user'),
    path('view-profile/', ViewProfileAPIView.as_view(), name='view-profile'),
    path('create-genre-pref/', CreateGenrePrefAPIView.as_view(), name='create-genre-pref'),

    # College & Course APIs
    path('create-college/', CollegeCreateView.as_view(), name='create-college'),
    path('view-college/', CollegeView.as_view(), name='view-college'),
    path('create-course/', CourseCreateView.as_view(), name='create-course'),
    path('view-course/', CourseView.as_view(), name='view-course'),

    # Book Management APIs
    path('view-books/', BookAPIView.as_view(), name='view-books'),
    path('create-book/', BookCreateView.as_view(), name='create-book'),
    path('update-book/', BookUpdateAPIView.as_view(), name='update-book'),
    path('delete-book/<int:pk>/', BookDeleteAPIView.as_view(), name='delete-book'),
    path('search-book/<str:query>', BookSearchAPIView.as_view(), name='search-book'),
    # path('get-genre/', GetGenreAPIView.as_view(), name='get-genre'),
    path('explore-books/', BookExploreAPIView.as_view(), name='explore-books'),

    # Cart Management APIs
    path('add-cart/', AddCartAPIView.as_view(), name='add-cart'),
    path('view-cart/', CartViewAPIView.as_view(), name='view-cart'),
    path('delete-cart/<int:pk>/', CartDeleteAPIView.as_view(), name='delete-cart'),

    # Post Management APIs
    path('view-posts/', PostAPIView.as_view(), name='view-posts'),
    path('add-wishlist/', AddWishlistAPIView.as_view(), name='add-wishlist'),
    path('create-wishlist/', CreateWishlistAPIView.as_view(), name='create-wishlist'),
    path('view-wishlist/', WishlistAPIView.as_view(), name='view-wishlist'),
    path('delete-wishlist/<int:pk>/', DeleteWishlistAPIView.as_view(), name='delete-wishlist'),

    #Rating Management APIs
    path('rate-app/', RatingCreateView.as_view(), name='rate-app'),
    path('view-ratings/', RatingAPIView.as_view(), name='view-ratings'),

    #Purchase Management APIs
    path('purchase-book/', PurchaseCreateAPIView.as_view(), name='purchase-book'),
    path('view-purchase/', PurchaseListAPIView.as_view(), name='view-purchase'),
    path('update-purchased-book/', UpdatePurchasedBookAPIView.as_view(), name='update-purchased-book'),

    #Genre Management APIs
    path('create-genre/', GenreCreateView.as_view(), name='create-genre'),
    path('view-genre/', GetGenreAPIView.as_view(), name='get-genre'),

    #Admin Management APIs
    path('view-users/', ViewUsersAPIView.as_view(), name='view-user'),
    path('view-transactions/', ViewTransaction.as_view(), name='view-transactions'),
    path('approve-transaction/', ApproveTransaction.as_view(), name='approve-transaction'),
    path('view-data-stats/', DataStatisticsAPIView.as_view(), name='view-data-stats'),
    path('gayson-donatenen/', CreateDonorAPIView.as_view(), name='gayson-donatenen'),
    path('to-verify-list/', ToVerifyUserAPIView.as_view(), name='to-verify-list'),
    path('verify-user/', VerifyUserAPIView.as_view(), name='verify-user'),
    path('decline-transaction/<int:pk>/', DeclineTransaction.as_view(), name='decline-transaction'),
    path('change-password/', UpdateTargetUser.as_view(), name='change-password'),

    
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)