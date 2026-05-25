from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError('Email is required.')
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email        = models.EmailField(unique=True)
    full_name    = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    farm_name    = models.CharField(max_length=150)
    country      = models.CharField(max_length=100)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
