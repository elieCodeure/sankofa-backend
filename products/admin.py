from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Country

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    list_editable = ('is_active',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_fr', 'seller', 'category', 'price', 'country', 'stock_quantity', 'stock_status', 'is_active', 'image_preview')
    list_filter = ('category', 'country', 'is_active', 'created_at', 'seller')
    search_fields = ('name_fr', 'name_en', 'description_fr', 'description_en', 'seller__email')
    readonly_fields = ('image_preview',)
    list_editable = ('price', 'stock_quantity', 'is_active')

    def stock_status(self, obj):
        if obj.stock_quantity <= 0:
            return format_html('<span style="color: #ef4444; font-weight: bold;">RUPTURE</span>')
        if obj.is_low_stock:
            return format_html('<span style="color: #f59e0b;">STOCK FAIBLE</span>')
        return format_html('<span style="color: #10b981;">EN STOCK</span>')
    
    stock_status.short_description = 'Statut Stock'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "Aucune image"
    
    image_preview.short_description = 'Aperçu'
