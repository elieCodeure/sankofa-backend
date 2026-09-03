from rest_framework import serializers
from .models import ConnectionRequest
from accounts.models import CustomUser

class SellerSimpleSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='profile.business_name', read_only=True)
    phone_number = serializers.CharField(source='profile.phone_number', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'business_name', 'phone_number')

class ConnectionRequestSerializer(serializers.ModelSerializer):
    sender_details = SellerSimpleSerializer(source='sender', read_only=True)
    receiver_details = SellerSimpleSerializer(source='receiver', read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ('id', 'sender', 'sender_details', 'receiver', 'receiver_details', 'status', 'created_at')
        read_only_fields = ('sender',)
