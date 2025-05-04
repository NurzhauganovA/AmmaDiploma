from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from .managers import UserManager


phone_number_validator = RegexValidator(
    regex=r'^\+7\d{10}$',
    message='Phone number must start with "+7" followed by 10 digits.',
    code='invalid_phone_number'
)


USER_ROLES = (
    ('admin', 'Администратор'),
    ('guest', 'Гость'),
    ('pregnant', 'Беременная'),
)


class User(PermissionsMixin, AbstractBaseUser):
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='guest')
    full_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True, unique=True)
    mobile_phone = models.CharField(max_length=25, unique=True, validators=[phone_number_validator])
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "mobile_phone"
    REQUIRED_FIELDS = ['role', 'full_name', 'password', 'email']

    def __str__(self):
        return self.mobile_phone

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'users'


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_info')
    photo_avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    iin = models.CharField(max_length=12, blank=True, null=True, unique=True)
    issued_by = models.CharField(max_length=100, blank=True, null=True)
    issued_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def empty_fields(self):
        fields = [
            self.photo_avatar,
            self.user.full_name,
            self.user.email,
            self.user.mobile_phone,
            self.country
        ]
        empty_count = len([field for field in fields if not field])
        return empty_count

    def __str__(self):
        return self.user.mobile_phone

    class Meta:
        verbose_name = 'Информация о пользователе'
        verbose_name_plural = 'Информация о пользователях'
        db_table = 'users_info'
        ordering = ['user']
