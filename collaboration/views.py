from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ConnectionRequest
from .serializers import ConnectionRequestSerializer, SellerSimpleSerializer
from accounts.models import CustomUser
from django.db.models import Q

class SellerListView(generics.ListAPIView):
    serializer_class = SellerSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return all sellers except the current user
        return CustomUser.objects.filter(role='SELLER').exclude(id=self.request.user.id)

class ConnectionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return requests where the user is either sender or receiver
        return ConnectionRequest.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        conn_request = self.get_object()
        if conn_request.receiver != request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        conn_request.status = 'ACCEPTED'
        conn_request.save()
        return Response({"status": "Accepted"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        conn_request = self.get_object()
        if conn_request.receiver != request.user:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        conn_request.status = 'REJECTED'
        conn_request.save()
        return Response({"status": "Rejected"})
