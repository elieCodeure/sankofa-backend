from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipmentViewSet, RouteViewSet, TransporterViewSet

router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'transporters', TransporterViewSet, basename='transporter')

urlpatterns = [
    path('', include(router.urls)),
]
