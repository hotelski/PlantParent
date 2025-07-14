from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    # Set the model to be managed
    model = User
    # Fields shown in the list view of users
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    # Add filters on the right sidebar in the admin user list view
    list_filter = ('is_staff', 'is_active', 'groups')
    # Enable search functionality for these fields
    search_fields = ('email', 'first_name', 'last_name')
    # Default sorting by email
    ordering = ('email',)
    
    # Fields when editing an existing user
    # This controls how the edit form for a user looks in the Django admin
    # Grouped in logical sections: personal info, permissions, dates, etc.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 
                'last_name', 
                'phone', 
                'address', 
                'city', 
                'postal_code', 
                'country',
                'profile_picture',
                'receive_newsletter'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields when adding a new user
    # Defines a simplified form when creating a new user in the admin panel.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'password1', 
                'password2', 
                'is_staff', 
                'is_active'
            ),
        }),
    )
    
    # Adds custom bulk actions to the admin UI
    actions = ['make_staff', 'remove_staff']

    # Adds two custom bulk actions in the user list:
    # "Mark selected users as staff"
    # "Remove staff status from selected users"
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)
    make_staff.short_description = "Mark selected users as staff"
    
    def remove_staff(self, request, queryset):
        queryset.update(is_staff=False)
    remove_staff.short_description = "Remove staff status from selected users"

# Registers the User model with the custom admin class so Django uses it in the admin panel.
admin.site.register(User, CustomUserAdmin)