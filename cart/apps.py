from django.apps import AppConfig


class CartConfig(AppConfig):
    # Set the default primary key type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # Define the name of the app (used internally by Django)
    name = 'cart'
