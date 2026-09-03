from rest_framework import viewsets, permissions, filters
from .models import Category, Product, Country
from .serializers import CategorySerializer, ProductSerializer, CountrySerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.filter(is_active=True)
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category', 'seller', 'seller__profile', 'country')
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name_fr', 'name_en', 'description_fr', 'description_en']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Marketplace filter: Only show products from users with role 'SELLER'
        if self.action == 'list' and self.request.query_params.get('my_products') != 'true':
            queryset = queryset.filter(seller__role='SELLER')

        # Filter by Category (slug or id)
        category_param = self.request.query_params.get('category')
        if category_param and category_param not in ['all', 'undefined']:
            if category_param.isdigit():
                queryset = queryset.filter(category_id=category_param)
            else:
                queryset = queryset.filter(category__slug=category_param)

        # Filter by Country (ID or Name)
        country_param = self.request.query_params.get('country')
        if country_param and country_param not in ['all', 'undefined']:
            if country_param.isdigit():
                queryset = queryset.filter(country_id=country_param)
            else:
                queryset = queryset.filter(country__name=country_param)
            
        # Filter by Price Range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price and min_price != 'undefined':
            queryset = queryset.filter(price__gte=min_price)
        if max_price and max_price != 'undefined':
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter by Currency
        currency_param = self.request.query_params.get('currency')
        if currency_param and currency_param not in ['all', 'undefined']:
            queryset = queryset.filter(currency=currency_param)
            
        # Dashboard Seller filter
        if self.request.query_params.get('my_products') == 'true' and self.request.user.is_authenticated:
            queryset = Product.objects.filter(seller=self.request.user)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
