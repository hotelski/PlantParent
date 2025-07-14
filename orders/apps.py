from django.apps import AppConfig


class OrdersConfig(AppConfig):
    # Use BigAutoField as the default primary key type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # Register the app under the name 'orders'
    name = 'orders'
