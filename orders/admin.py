from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Order, OrderItem

# Inline admin for OrderItem (shown inside Order admin page)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Do not show extra blank rows by default
    extra = 0
    # Fields to display in the inline table
    readonly_fields = ('product_link', 'price', 'quantity', 'total_price_display')
    fields = ('product_link', 'price', 'quantity', 'total_price_display')

    # Show link to the related product
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'

    # Display total price for each item
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total'

# Main admin class for Order
class OrderAdmin(admin.ModelAdmin):
    # Fields shown in the order list view
    list_display = (
        'order_id',
        'user_email',
        'status_badge',
        'total_paid_display',
        'item_count',
        'created_at',
        'updated_at',
        'status'
    )
    # Sidebar filters
    list_filter = (
        'status',
        'created_at',
        'updated_at',
        'shipping_country'
    )
    # Fields included in search
    search_fields = (
        'id',
        'user__email',
        'user__first_name',
        'user__last_name',
        'shipping_address',
        'stripe_payment_intent'
    )
    # Allow inline editing of status directly from the list view
    list_editable = ('status',)
    # Fields visible but not editable in the admin form
    readonly_fields = (
        'order_id',
        'user_link',
        'created_at',
        'updated_at',
        'stripe_payment_intent',
        'total_paid_display',
        'item_count',
        'order_summary'
    )
    # Organize fields into sections
    fieldsets = (
        (None, {
            'fields': ('order_id', 'user_link', 'status')
        }),
        ('Payment', {
            'fields': ('stripe_payment_intent', 'total_paid_display')
        }),
        ('Shipping', {
            'fields': (
                'shipping_address',
                'shipping_city',
                'shipping_postal_code',
                'shipping_country'
            )
        }),
        ('Items', {
            'fields': ('item_count', 'order_summary')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    # Add inline table of order items
    inlines = [OrderItemInline]

    # Format order ID
    def order_id(self, obj):
        return f"Order #{obj.id}"
    order_id.short_description = 'Order ID'

    # Show user's email
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

    # Make user email a clickable link to their admin profile
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'

    # Show colored badge based on order status
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors[obj.status],
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    # Display total paid in dollars
    def total_paid_display(self, obj):
        return f"${obj.total_paid:.2f}"
    total_paid_display.short_description = 'Total Paid'

    # Display total number of items
    def item_count(self, obj):
        return obj.total_items
    item_count.short_description = 'Items'

    # Display HTML summary of all items in the order
    def order_summary(self, obj):
        items = obj.items.select_related('product')
        html = '<table class="table"><thead><tr><th>Product</th><th>Price</th><th>Qty</th><th>Total</th></tr></thead><tbody>'
        for item in items:
            html += f'<tr><td>{item.product.name}</td><td>${item.price:.2f}</td><td>{item.quantity}</td><td>${item.total_price:.2f}</td></tr>'
        html += f'<tr><td colspan="3"><strong>Total</strong></td><td><strong>${obj.total_paid:.2f}</strong></td></tr>'
        html += '</tbody></table>'
        return format_html(html)
    order_summary.short_description = 'Order Details'

# Admin for individual OrderItem
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order_link',
        'product_link',
        'price_display',
        'quantity',
        'total_price_display'
    )
    list_filter = ('order__status', 'order__created_at')
    search_fields = (
        'order__id',
        'product__name',
        'order__user__email'
    )
    readonly_fields = ('order_link', 'product_link', 'price_display', 'total_price_display')

    # Clickable link to order in admin
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order__id'

    # Clickable link to product
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'

    # Price fields
    def price_display(self, obj):
        return f"${obj.price:.2f}"
    price_display.short_description = 'Price'
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total'

# Register models
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)