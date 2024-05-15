from django.db import models
from django.utils import timezone
from authentication.models import User
from book_management.models import Book

class Purchase_History(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    seller = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="seller")
    purchase_book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(default=timezone.now)
    transaction_hash = models.CharField(max_length=255)
