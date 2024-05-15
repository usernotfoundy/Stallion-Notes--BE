from rest_framework import serializers
from .models import *
from authentication.models import User
from book_management.models import Book

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    # seller_user = serializers.PrimaryKeyRelatedField(source='book.seller', queryset=User.objects.all())

    class Meta:
        model = Cart
        fields = '__all__'
        # extra_kwargs = {

        # }