from django.apps import AppConfig


class BlogConfig(AppConfig):
    # Set the default primary key field type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # Specify the full Python path to the app
    name = 'blog'
