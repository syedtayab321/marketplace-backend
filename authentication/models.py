from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone
import random


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, phone_number=None, password=None, user_type='buyer'):
        if not email and not phone_number:
            raise ValueError('Users must have either an email or a phone number.')

        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, phone_number=phone_number, user_type=user_type)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email=email, password=password, user_type='admin')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    is_active = models.BooleanField(default=False)  # Activated only after OTP verification
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="authentication_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="authentication_user_permissions", blank=True)

    objects = UserManager()

    # Allow login using either email or phone_number
    USERNAME_FIELD = 'email'  # Default login field
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email if self.email else self.phone_number


class OTPVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="otp_verification")
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)

    def is_expired(self):
        """Check if the OTP has expired (valid for 5 minutes)."""
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def generate_otp(self):
        """Generate and save a new OTP code."""
        self.otp_code = str(random.randint(100000, 999999))
        self.created_at = timezone.now()  # Reset creation time
        self.save()
        return self.otp_code
