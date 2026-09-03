from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('CLIENT', 'Client'),
        ('SELLER', 'Vendeur'),
        ('TRANSPORTER', 'Expéditeur'),
    )

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CLIENT')
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    id_card = models.FileField(upload_to='identity_docs/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    # Champ motif de rejet simple
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Motif de rejet")
    # Seller specific
    business_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Transporter specific
    VEHICLE_CHOICES = (
        ('MOTORCYCLE', 'Vélomoteur'),
        ('VAN', 'Camionnette'),
        ('TRUCK', 'Camion'),
        ('OTHER', 'Autre'),
    )
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, blank=True, null=True)
    coverage_area = models.TextField(blank=True, null=True, help_text="Zones ou villes desservies")
    
    # Common fields
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.email} ({self.user.role})"
