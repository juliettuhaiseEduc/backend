from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, password=None, **extra):
        if not extra.get('email') and not extra.get('phone_number'):
            raise ValueError('Email or phone number is required.')
        if extra.get('email'):
            extra['email'] = self.normalize_email(extra['email'])
        user = self.model(**extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(password=password, email=email, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    email        = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    full_name    = models.CharField(max_length=150)
    farm_name    = models.CharField(max_length=150, blank=True, default='')
    country      = models.CharField(max_length=100, blank=True, default='')
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    weather_access  = models.BooleanField(default=True)  # admin can revoke
    created_at   = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email or self.phone_number or str(self.id)
