from django.db import models
from django.conf import settings
from orders.models import Order

class Route(models.Model):
    transporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='routes')
    origin = models.CharField(max_length=100, help_text="Ville de départ")
    destination = models.CharField(max_length=100, help_text="Ville d'arrivée")
    frequency = models.CharField(max_length=100, help_text="Ex: Hebdomadaire, Quotidien", blank=True, null=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pricing_mode = models.CharField(max_length=20, choices=[('flat', 'Flat'), ('per_category', 'Per Category')], default='flat')
    category_prices = models.JSONField(default=list, blank=True)
    product_exceptions = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.origin} -> {self.destination} ({self.transporter.email})"

class Shipment(models.Model):
    STATUS_CHOICES = (
        ('REQUESTED', 'Demande envoyée'),
        ('ACCEPTED', 'Acceptée par le transporteur'),
        ('PICKED_UP', 'Colis récupéré'),
        ('IN_TRANSIT', 'En cours de route'),
        ('DELIVERED', 'Livré'),
        ('CANCELLED', 'Annulé'),
    )

    SHIPMENT_TYPES = (
        ('MARKETPLACE', 'Commande Marketplace'),
        ('PERSONAL', 'Envoi Personnel'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment', null=True, blank=True)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='initiated_shipments',
        null=True, blank=True
    )
    shipment_type = models.CharField(max_length=20, choices=SHIPMENT_TYPES, default='MARKETPLACE')
    transporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='shipments_to_handle',
        limit_choices_to={'role': 'TRANSPORTER'}
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    description = models.TextField(blank=True, null=True, help_text="Contenu du colis")
    origin = models.CharField(max_length=255, blank=True, null=True, help_text="Lieu de ramassage")
    destination = models.CharField(max_length=255, blank=True, null=True, help_text="Lieu de livraison")
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Poids en kg")
    tracking_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    verification_code = models.CharField(max_length=10, blank=True, null=True, help_text="Code pour valider la livraison")
    estimated_delivery = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment {self.id} - {self.status}"
