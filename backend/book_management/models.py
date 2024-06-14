from django.db import models
from django.utils import timezone
from authentication.models import User

# Create your models here.
# class Author(models.Model):
#     first_name = models.CharField(max_length=125)
#     middle_name = models.CharField(max_length=125)
#     last_name = models.CharField(max_length=125)

class Genre(models.Model):
    genre_name = models.CharField(max_length=125)
    
class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    isbn = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    description = models.TextField()
    status_book = models.CharField(max_length=50) #upload processing
    # availability = models.BooleanField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # upload_status = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING, null=True, blank=True)
    book_img = models.ImageField(upload_to='books', blank=True, null=True)
    wishlist = models.BigIntegerField(default=0)

class MyWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
