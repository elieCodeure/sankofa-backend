from rest_framework import serializers
from .models import Category, Product, Country

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    seller_name = serializers.CharField(source='seller.profile.business_name', read_only=True)
    seller_email = serializers.CharField(source='seller.email', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name_fr', 'name_en', 'description_fr', 'description_en', 
                 'price', 'currency', 'stock_quantity', 'stock_threshold', 
                 'category', 'category_name', 'seller', 'seller_name', 'seller_email',
                 'country', 'country_name', 'image', 'span', 'tag_fr', 'tag_en',
                 'is_low_stock', 'is_active', 'created_at')
        read_only_fields = ('seller',)
