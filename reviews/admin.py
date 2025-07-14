from django.contrib import admin
from django.utils.html import format_html
from .models import Review

# Custom admin interface for user reviews
class ReviewAdmin(admin.ModelAdmin):
    # Fields displayed in the list view
    list_display = (
        # Product being reviewed
        'product',
        # User who left the review
        'user',
        # Star rating (visual)
        'rating_stars',
        # Preview of the comment
        'short_comment',
        # Whether the review is published
        'approved',
        'created_at',
        'updated_at'
    )
    # Sidebar filters
    list_filter = (
        'approved',
        'rating',
        'created_at',
        'updated_at',
        'product'
    )
    # Search by related fields and comment text
    search_fields = (
        'product__name',
        'user__email',
        'user__first_name',
        'user__last_name',
        'comment'
    )
    # Allow editing "approved" status directly in list view
    list_editable = ('approved',)
    # Read-only fields in the review form
    readonly_fields = (
        'product',
        'user',
        'rating_stars',
        'created_at',
        'updated_at',
        'full_comment'
    )
    # Group fields into logical sections
    fieldsets = (
        (None, {
            'fields': ('product', 'user', 'rating_stars')
        }),
        ('Review Content', {
            'fields': ('full_comment',)
        }),
        ('Moderation', {
            'fields': ('approved',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # Display star rating using HTML
    # get_rating_display() returns the display value for a choice field (e.g., "★★★★★")
    def rating_stars(self, obj):
        return format_html(
            '<span style="color: gold; font-size: 1.2em;">{}</span>',
            obj.get_rating_display()
        )
    rating_stars.short_description = 'Rating'

    # Show only the first 50 characters of the comment
    def short_comment(self, obj):
        return obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')
    short_comment.short_description = 'Comment Preview'

    #  Render full comment in a styled box
    def full_comment(self, obj):
        return format_html(
            '<div style="padding: 10px; border: 1px solid #eee; border-radius: 5px;">{}</div>',
            obj.comment
        )
    full_comment.short_description = 'Full Comment'

# Register the Review model with custom admin
admin.site.register(Review, ReviewAdmin)