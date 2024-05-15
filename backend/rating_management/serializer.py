from rest_framework import serializers
from .models import *
from authentication.serializer import UserSerializer

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Rating
        fields = '__all__'