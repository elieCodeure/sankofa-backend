from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConnectionRequestViewSet, SellerListView

router = DefaultRouter()
router.register(r'requests', ConnectionRequestViewSet, basename='connection-request')

urlpatterns = [
    path('sellers/', SellerListView.as_view(), name='seller-list'),
    path('', include(router.urls)),
]
