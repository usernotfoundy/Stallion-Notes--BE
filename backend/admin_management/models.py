from django.db import models
from django.utils import timezone
from authentication.models import User
from book_management.models import Book

class Donor(models.Model):
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=128)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)

