from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    # Use BigAutoField as the default type for auto-incrementing primary keys
    default_auto_field = 'django.db.models.BigAutoField'
    # The full Python path to the app
    name = 'reviews'
