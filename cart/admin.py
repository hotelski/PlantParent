from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Cart, CartItem

# This admin file provides:
# Inline display of cart items in cart detail
# Rich table rendering of cart contents
# Direct links to related User and Product models
# Read-only fields for safer management
# Custom filters and search by email, product name, and date

# Inline display of cart items inside the Cart admin
class CartItemInline(admin.TabularInline):
    model = CartItem
    # Don't show any extra empty forms
    extra = 0
    readonly_fields = ('product_link', 'current_price', 'quantity', 'total_price_display', 'added_at')
    fields = ('product_link', 'current_price', 'quantity', 'total_price_display', 'added_at')

    # Custom display fields
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    
    def current_price(self, obj):
        return f"${obj.product.price:.2f}"
    current_price.short_description = 'Unit Price'
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total'

# CartAdmin – Display and manage carts in the admin
class CartAdmin(admin.ModelAdmin):
    list_display = (
        'user_email',
        'total_items',
        'total_value',
        'created_at',
        'updated_at',
        'cart_link'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name'
    )
    readonly_fields = (
        'user_link',
        'created_at',
        'updated_at',
        'total_items',
        'total_value_display',
        'cart_contents'
    )
    inlines = [CartItemInline]

    # Custom display helpers
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'

    # Cart summary and links
    def total_items(self, obj):
        return obj.total_quantity
    total_items.short_description = 'Items'
    
    def total_value(self, obj):
        return f"${obj.total_price:.2f}"
    total_value.short_description = 'Total Value'
    total_value.admin_order_field = 'total_price'
    
    def total_value_display(self, obj):
        return self.total_value(obj)
    total_value_display.short_description = 'Total Value'
    
    def cart_link(self, obj):
        url = reverse('admin:cart_cart_change', args=[obj.id])
        return format_html('<a href="{}">View Cart</a>', url)
    cart_link.short_description = 'Actions'

    # Render cart contents as HTML table
    def cart_contents(self, obj):
        items = obj.items.select_related('product')
        if not items:
            return "Cart is empty"
        
        html = '''
        <table class="table">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for item in items:
            html += f'''
            <tr>
                <td>{item.product.name}</td>
                <td>${item.product.price:.2f}</td>
                <td>{item.quantity}</td>
                <td>${item.total_price:.2f}</td>
            </tr>
            '''
        
        html += f'''
            <tr style="font-weight: bold;">
                <td colspan="3">Total</td>
                <td>${obj.total_price:.2f}</td>
            </tr>
            </tbody>
        </table>
        '''
        return format_html(html)
    cart_contents.short_description = 'Cart Contents'

# Manage individual items directly
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'user_email',
        'product_link',
        'current_price',
        'quantity',
        'total_price_display',
        'added_at'
    )
    list_filter = ('added_at', 'product__category')
    search_fields = (
        'cart__user__email',
        'product__name',
        'product__description'
    )
    readonly_fields = (
        'cart_link',
        'product_link',
        'current_price',
        'total_price_display',
        'added_at'
    )

    # Field display methods
    def user_email(self, obj):
        return obj.cart.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'cart__user__email'
    
    def cart_link(self, obj):
        url = reverse('admin:cart_cart_change', args=[obj.cart.id])
        return format_html('<a href="{}">Cart #{}</a>', url, obj.cart.id)
    cart_link.short_description = 'Cart'
    
    def product_link(self, obj):
        url = reverse('admin:products_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    
    def current_price(self, obj):
        return f"${obj.product.price:.2f}"
    current_price.short_description = 'Price'
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = 'Total'

# Register models with admin site
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)