from rest_framework import serializers
from .models import Shipment, Route
from accounts.models import CustomUser

class TransporterSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='profile.business_name', read_only=True)
    vehicle_type = serializers.CharField(source='profile.vehicle_type', read_only=True)
    coverage_area = serializers.CharField(source='profile.coverage_area', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'business_name', 'vehicle_type', 'coverage_area')

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'
        read_only_fields = ('transporter',)

class ShipmentSerializer(serializers.ModelSerializer):
    transporter_details = TransporterSerializer(source='transporter', read_only=True)
    client_name = serializers.CharField(source='client.first_name', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)

    class Meta:
        model = Shipment
        fields = ('id', 'order', 'client', 'client_name', 'client_email', 'shipment_type', 'transporter', 'transporter_details', 'status', 'description', 'origin', 'destination', 'weight', 'tracking_number', 'verification_code', 'estimated_delivery', 'created_at')
        read_only_fields = ('client', 'verification_code')
