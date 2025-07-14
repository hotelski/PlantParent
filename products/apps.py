from django.apps import AppConfig


class ProductsConfig(AppConfig):
    # Use BigAutoField as the default primary key type for models
    default_auto_field = 'django.db.models.BigAutoField'
    # Register this app under the name 'products'
    name = 'products'
