from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from products.models import Product
from .notifications import send_order_notifications

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        items_data = self.request.data.get('items', [])
        shipping_address = self.request.data.get('shipping_address')
        phone_number = self.request.data.get('phone_number')
        
        order = serializer.save(
            user=self.request.user, 
            shipping_address=shipping_address,
            phone_number=phone_number,
            status='PAID' # For mock flow
        )
        
        total = 0
        for item in items_data:
            try:
                product_id = item.get('product_id')
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item['product_name'],
                    quantity=item.get('quantity', 1),
                    price=item['price']
                )
                total += float(item['price']) * int(item.get('quantity', 1))
            except Product.DoesNotExist:
                # Fallback if product is missing, at least save the name/price
                OrderItem.objects.create(
                    order=order,
                    product=None,
                    product_name=item['product_name'],
                    quantity=item.get('quantity', 1),
                    price=item['price']
                )
                total += float(item['price']) * int(item.get('quantity', 1))
            except Exception as e:
                print(f"Error processing order item: {e}")
                continue
        
        order.total_price = total
        order.save()
        
        # Trigger notifications (PDF + Email)
        send_order_notifications(order)

class SellerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return orders that contain at least one product owned by this seller
        return Order.objects.filter(items__product__seller=self.request.user).distinct().order_by('-created_at')

class DelegateShippingView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        
        # Verify the order belongs to the user
        if order.user != request.user:
            return Response({"detail": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)
            
        if order.status != "PAID":
            return Response(
                {"detail": "Seule une commande payée et non encore expédiée peut être confiée au vendeur."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.shipping_delegated = True
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
