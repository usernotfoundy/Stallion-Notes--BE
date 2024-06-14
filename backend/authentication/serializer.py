from rest_framework import serializers
from .models import User, College, Course, Misc

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
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)
    is_verified = serializers.BooleanField(default=False)
    is_flag = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'profile_img', 'course', 'is_staff', 'is_superuser', 'is_verified', 'is_flag']
        extra_kwargs = {'password': {'write_only': True, 'required': False}, 'course': {'required': False}, 'profile_img': {'required': False}, 'phone_number': {'required': False}}

    def create(self, validated_data):
        course_data = validated_data.pop('course', None)
        is_staff_data = validated_data.pop('is_staff', False)
        is_superuser_data = validated_data.pop('is_superuser', False)
        is_verified_data = validated_data.pop('is_verified', False)
        is_flag_data = validated_data.pop('is_flag', False)

        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            middle_name=validated_data.get('middle_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            profile_img=validated_data.get('profile_img', ''),
            course=course_data,
            is_staff=is_staff_data,
            is_superuser=is_superuser_data,
            is_verified=is_verified_data,
            is_flag=is_flag_data
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

class MiscSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Misc
        fields = '__all__'

