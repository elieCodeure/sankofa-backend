import random
import string
from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Shipment, Route
from .serializers import ShipmentSerializer, RouteSerializer, TransporterSerializer
from accounts.models import CustomUser

class TransporterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransporterSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return CustomUser.objects.filter(role='TRANSPORTER', profile__is_verified=True)

class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Route.objects.filter(transporter=self.request.user)

    def perform_create(self, serializer):
        serializer.save(transporter=self.request.user)

class ShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'TRANSPORTER':
            return Shipment.objects.filter(transporter=user)
        return Shipment.objects.filter(client=user)

    def perform_create(self, serializer):
        # Generate a random verification code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        shipment = serializer.save(client=self.request.user, verification_code=code)
        
        # Auto-update order status if linked
        order = serializer.validated_data.get('order')
        if order:
            order.status = 'SHIPPED'
            order.save()

        # Send email to the client with the verification code
        client_email = self.request.user.email
        transporter_email = shipment.transporter.email
        
        try:
            # Notify Client
            send_mail(
                subject='Sankhofa - Votre code de livraison',
                message=f'Bonjour,\n\nVotre demande d\'expédition a été créée avec succès.\n\nLe code secret à remettre au transporteur lors de la réception de votre colis est : {code}\n\nNe partagez ce code avec le transporteur qu\'une fois le colis reçu.\n\nMerci,\nL\'équipe Sankhofa',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[client_email],
                fail_silently=True,
            )
            # Notify Transporter
            send_mail(
                subject='Sankhofa - Nouvelle course assignée',
                message=f'Bonjour,\n\nVous avez une nouvelle expédition à prendre en charge pour {self.request.user.first_name}.\n\nConnectez-vous à votre tableau de bord pour accepter la course et gérer le statut.\n\nMerci,\nL\'équipe Sankhofa',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[transporter_email],
                fail_silently=True,
            )
        except Exception as e:
            pass

    @decorators.action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        shipment = self.get_object()
        new_status = request.data.get('status')
        
        if shipment.transporter != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            
        if new_status not in dict(Shipment.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            
        shipment.status = new_status
        
        # If closing the shipment, maybe we need the code?
        if new_status == 'DELIVERED':
            code_provided = request.data.get('verification_code')
            if shipment.verification_code and code_provided != shipment.verification_code:
                return Response({"error": "Verification code incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Also update the order status
            if shipment.order:
                shipment.order.status = 'DELIVERED'
                shipment.order.save()

        shipment.save()
        return Response(ShipmentSerializer(shipment).data)
