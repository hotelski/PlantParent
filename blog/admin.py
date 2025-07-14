from django.contrib import admin
from .models import BlogPost

class BlogPostAdmin(admin.ModelAdmin):
    # Fields to show in the list view (table view in admin)
    list_display = ('title', 'author', 'created_at', 'published')
    # Add sidebar filters in the admin interface
    list_filter = ('published', 'created_at', 'author')
    # Enable search functionality on title and content fields
    search_fields = ('title', 'content')
    # Automatically fill the slug field based on the title
    prepopulated_fields = {'slug': ('title',)}
    # Make these fields read-only in the form
    readonly_fields = ('created_at', 'updated_at')
    # Form layout in the admin panel
    # This defines how the form is grouped into sections in the admin panel.
    # Sections: general info, media, publishing options.
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Publishing', {
            'fields': ('published', 'created_at', 'updated_at')
        }),
    )

    # Permissions (all enabled manually)
    # These methods override the default permission logic, granting full access to any user with admin access.
    # This is useful for debugging or simplifying permission control — but should be restricted in production if needed.
    def has_module_permission(self, request):
        return True
        
    def has_add_permission(self, request):
        return True
        
    def has_change_permission(self, request, obj=None):
        return True
        
    def has_delete_permission(self, request, obj=None):
        return True
        
    def has_view_permission(self, request, obj=None):
        return True

# Makes BlogPost visible and manageable in the Django admin interface using the customized configuration.
admin.site.register(BlogPost, BlogPostAdmin)