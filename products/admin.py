from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

# Admin interface for product categories
class CategoryAdmin(admin.ModelAdmin):
    # Fields to show in the list view
    list_display = ('name', 'slug', 'display_image', 'product_count')
    # Filter sidebar
    list_filter = ('name',)
    # Enable search by name or description
    search_fields = ('name', 'description')
    # Auto-generate slug based on name
    prepopulated_fields = {'slug': ('name',)}
    # Fields that are read-only
    readonly_fields = ('display_image',)

    # Show thumbnail preview of category image
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image Preview'

    # Show how many products are in the category
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products Count'

# Admin interface for products
# Fields shown in the admin list view
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'category', 
        'price', 
        'stock', 
        'available', 
        'featured', 
        'display_image',
        'created'
    )
    # Sidebar filters
    list_filter = ('available', 'featured', 'category', 'created')
    # Search fields
    search_fields = ('name', 'description', 'category__name')
    # Allow inline editing in the list view
    list_editable = ('price', 'stock', 'available', 'featured')
    # Auto-generate slug from name
    prepopulated_fields = {'slug': ('name',)}
    # Fields that are read-only in the form
    readonly_fields = ('display_image', 'created', 'updated')
    # Organize fields into admin form sections
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'price')
        }),
        ('Inventory', {
            'fields': ('stock', 'available', 'featured')
        }),
        ('Content', {
            'fields': ('description', 'short_description')
        }),
        ('Media', {
            'fields': ('image', 'display_image')
        }),
        ('Dates', {
            'fields': ('created', 'updated')
        }),
    )

    # Show product image thumbnail in admin
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image Preview'

# Register both models with custom admin classes
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)