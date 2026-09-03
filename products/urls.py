from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, CountryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'', ProductViewSet) # Base product URL

urlpatterns = [
    path('', include(router.urls)),
]
