from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product_name', 'quantity', 'price')
    readonly_fields = ('product_name', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__email', 'phone_number', 'shipping_address')
    inlines = [OrderItemInline]
    list_editable = ('status',)

    def has_add_permission(self, request):
        # Prevent adding orders manually for now to keep integrity
        return False

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_name', 'quantity', 'price')
    list_filter = ('product__category', 'price')
    search_fields = ('product_name', 'order__id', 'order__user__email')
