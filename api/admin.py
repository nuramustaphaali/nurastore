from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'price', 'quantity')
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'payment_method', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'created_at')
    search_fields = ('user__username', 'id', 'payment_reference')
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount',)
    
    # Action to quickly mark as Shipped
    actions = ['mark_as_shipped']

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        # Note: Bulk update doesn't trigger signals, so save individually if you want emails
        for order in queryset:
            order.status = 'shipped'
            order.save() # This triggers the email signal
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
