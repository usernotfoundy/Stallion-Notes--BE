from rest_framework import serializers
from .models import *
from authentication.models import User
from book_management.models import Book

class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    purchase_book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    seller = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Purchase_History
        fields = '__all__'
        extra_kwargs = { 
                        # 'purchase_book': {'allow_null': True, 'required': False},
                        'created_at': {'allow_null': True, 'required': False},
                        'transaction_hash': {'allow_null': True, 'required': False},
                         }
        