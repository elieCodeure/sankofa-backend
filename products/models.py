from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=5, blank=True, null=True, help_text="Code ISO (ex: SN, GH)")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"

class Product(models.Model):
    SPAN_CHOICES = (
        ('square', 'Carré'),
        ('tall', 'Vertical'),
        ('wide', 'Large'),
        ('large', 'Grand Carré'),
    )


    name_fr = models.CharField(max_length=255, verbose_name="Nom (FR)")
    name_en = models.CharField(max_length=255, verbose_name="Nom (EN)", blank=True, null=True)
    description_fr = models.TextField(verbose_name="Description (FR)")
    description_en = models.TextField(verbose_name="Description (EN)", blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='EUR')
    
    stock_quantity = models.PositiveIntegerField(default=0)
    stock_threshold = models.PositiveIntegerField(default=5, help_text="Alerte quand le stock descend sous ce seuil")
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Editorial fields
    span = models.CharField(max_length=20, choices=SPAN_CHOICES, default='square')
    tag_fr = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tag (FR)")
    tag_en = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tag (EN)")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name_fr

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.stock_threshold
