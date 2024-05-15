from django.db import models
from authentication.models import User
from book_management.models import Book


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    # seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='seller')
