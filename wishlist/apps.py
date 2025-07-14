from django.apps import AppConfig


class WishlistConfig(AppConfig):
    # Use BigAutoField for primary keys unless specified otherwise
    default_auto_field = 'django.db.models.BigAutoField'
    # Internal name of the app (used in INSTALLED_APPS, etc.)
    name = 'wishlist'
