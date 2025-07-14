from django.contrib import admin
from django.utils.html import format_html
from .models import Wishlist, WishlistItem

# Inline: Wishlist items inside wishlist admin view
class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    # No empty extra forms
    extra = 0
    # Show but don’t edit
    readonly_fields = ('added_at', 'product_link')
    # Show only these fields
    fields = ('product_link', 'added_at')

    # Render clickable product name
    def product_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            obj.product.get_absolute_url(),
            obj.product.name
        )
    product_link.short_description = 'Product'

# Admin panel for Wishlist itself
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        # Show user
        'user_email',
        # Number of items
        'item_count',
        'created_at',
        'updated_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name'
    )
    readonly_fields = ('created_at', 'updated_at')
    # Show WishlistItems inline
    inlines = [WishlistItemInline]

    # Show user’s email in admin
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

    # Number of items in wishlist
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items Count'

# Admin panel for individual wishlist items
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = (
        'user_email',
        'product_name',
        'product_price',
        'product_stock',
        'added_at'
    )
    list_filter = ('added_at', 'product__category')
    search_fields = (
        'wishlist__user__email',
        'product__name',
        'product__description'
    )
    readonly_fields = ('added_at', 'product_link')
    fields = ('wishlist', 'product_link', 'added_at')

    # Email of user who owns the wishlist
    def user_email(self, obj):
        return obj.wishlist.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'wishlist__user__email'

    # Display product data
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    product_name.admin_order_field = 'product__name'
    
    def product_price(self, obj):
        return f"${obj.product.price}"
    product_price.short_description = 'Price'
    product_price.admin_order_field = 'product__price'
    
    def product_stock(self, obj):
        return obj.product.stock
    product_stock.short_description = 'Stock'
    product_stock.admin_order_field = 'product__stock'

    # Clickable link to the product
    def product_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            obj.product.get_absolute_url(),
            obj.product.name
        )
    product_link.short_description = 'Product'

# Register both models in admin
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(WishlistItem, WishlistItemAdmin)