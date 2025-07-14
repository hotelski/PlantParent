from django.apps import AppConfig

# Define the configuration class for the 'accounts' app
class AccountsConfig(AppConfig):
    # Set the default primary key field type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # Specify the name of the app
    name = 'accounts'
