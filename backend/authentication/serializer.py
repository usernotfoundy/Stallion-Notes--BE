from rest_framework import serializers
from .models import User, College, Course

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['id', 'college_name', 'college_abbr']

class CourseSerializer(serializers.ModelSerializer):
    college = serializers.PrimaryKeyRelatedField(queryset=College.objects.all())

    class Meta:
        model = Course
        fields = ['id', 'college', 'course_name', 'course_abbr']


class UserSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'profile_img', 'course']
        extra_kwargs = {'password': {'write_only': True, 'required': False}, 'course': {'required': False}, 'profile_img': {'required': False}}

    def create(self, validated_data):
        course_data = validated_data.pop('course', None)

        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            middle_name = validated_data.get('middle_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            profile_img=validated_data.get('profile_img', ''),
            course=course_data,
        )
        user.set_password(validated_data['password'])
        user.save()

        return user
