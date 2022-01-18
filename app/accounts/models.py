import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                                        PermissionsMixin
from django.conf import settings
from django.utils.timezone import now

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new supersuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserType(models.Model):
    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True,
                          editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that suports using email instead username"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    cpf = models.CharField(max_length=30)
    phone = models.CharField(max_length=30)

    # Address Information
    street = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=20)
    complement = models.CharField(max_length=150, blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Job(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Employe(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hired_date = models.DateField(default=now)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    job = models.ForeignKey(Job, on_delete=models.PROTECT)
    

    def __str__(self):
        return self.user.name