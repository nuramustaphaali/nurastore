from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Product, Category, Order, OrderItem, Review, Cart

class LowStockFilter(admin.SimpleListFilter):
    title = 'Inventory Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Low Stock (< 10)'),
            ('out', 'Out of Stock (0)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(stock__lt=10, stock__gt=0)
        if self.value() == 'out':
            return queryset.filter(stock=0)
        return queryset

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_image', 'name', 'price', 'stock_status', 'is_available', 'sold_count')
    list_filter = ('is_available', 'category', LowStockFilter)
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available') # Edit price directly from list
    prepopulated_fields = {'slug': ('name',)}

    # A. Display Image Thumbnail
    def product_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    product_image.short_description = "Image"

    # B. Color-Coded Stock Alert
    def stock_status(self, obj):
        if obj.stock == 0:
            color = 'red'
            text = 'Out of Stock'
        elif obj.stock < 10:
            color = 'orange'
            text = f'Low ({obj.stock})'
        else:
            color = 'green'
            text = f'{obj.stock} Units'
            
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, text)
    stock_status.short_description = "Inventory"

    # C. Calculated Field: Total Sold
    def sold_count(self, obj):
        # Sum up quantity from delivered orders
        total = OrderItem.objects.filter(product=obj, order__status='delivered').aggregate(Sum('quantity'))['quantity__sum']
        return total or 0
    sold_count.short_description = "Units Sold"


    
from django.urls import reverse
from django.utils.safestring import mark_safe
from core.email_service import EmailService

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'price', 'quantity', 'subtotal')
    extra = 0
    can_delete = False

    def subtotal(self, obj):
        return f"₦{obj.price * obj.quantity}"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'total_amount', 'status_badge', 'payment_method', 'created_at', 'action_buttons')
    list_filter = ('status', 'is_paid', 'created_at', 'payment_method')
    search_fields = ('id', 'user__username', 'user__email', 'payment_reference')
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount', 'delivery_fee', 'created_at')
    
    actions = ['mark_processing', 'mark_shipped', 'resend_confirmation_email']

    # A. Link to User Profile
    def user_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "Customer"

    # B. Status Badge
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107', # Yellow
            'paid': '#17a2b8',    # Blue
            'processing': '#6610f2', # Purple
            'shipped': '#fd7e14', # Orange
            'delivered': '#28a745', # Green
            'cancelled': '#dc3545', # Red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 12px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display().upper()
        )
    status_badge.short_description = "Status"

    # C. Quick Action Buttons (HTML)
    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="/adminBest/api/order/{}/change/">Manage</a>',
            obj.id
        )
    action_buttons.short_description = "Actions"

    # D. Bulk Action: Resend Email
    def resend_confirmation_email(self, request, queryset):
        count = 0
        for order in queryset:
            # Trigger the email logic manually
            EmailService.send_order_status_email(order)
            count += 1
        self.message_user(request, f"Emails queued for {count} orders.")
    resend_confirmation_email.short_description = "Resend Email Notification"

    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
    
    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')

