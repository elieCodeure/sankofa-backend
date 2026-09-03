from django.contrib import admin
from .models import Shipment, Route

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'transporter', 'frequency', 'price_per_kg', 'is_active')
    list_filter = ('is_active', 'origin', 'destination', 'frequency')
    search_fields = ('transporter__email', 'origin', 'destination')

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'transporter', 'shipment_type', 'status', 'origin', 'destination', 'weight', 'tracking_number', 'created_at')
    list_filter = ('status', 'shipment_type', 'created_at')
    search_fields = ('tracking_number', 'client__email', 'transporter__email', 'origin', 'destination')
    list_editable = ('status', 'tracking_number')
    readonly_fields = ('verification_code',)
