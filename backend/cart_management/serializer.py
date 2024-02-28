from rest_framework import serializers
from .models import *
from authentication.models import User
from book_management.models import Book

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Cart
        fields = ['user', 'book']
        extra_kwargs = {'user': {'required':True, 'allow_blank':False},
                        'book': {'required':True, 'allow_blank':False}}