from rest_framework import serializers
from .models import *
from authentication.serializer import UserSerializer
from book_management.serializer import BookSerializer

class DonorSerializer(serializers.ModelSerializer):
    admin = serializers.HiddenField(default=serializers.CurrentUserDefault())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Donor
        fields = '__all__'