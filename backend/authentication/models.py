from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class College(models.Model):
    college_name = models.CharField(max_length=128)
    college_abbr = models.CharField(max_length=128)

class Course(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=128)
    course_abbr = models.CharField(max_length=128)

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    profile_img = models.ImageField(upload_to='rest_framework/img/profile', blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'username'

class Misc(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    genre_pref = models.CharField(max_length=255)
    author_pref = models.CharField(max_length=255)