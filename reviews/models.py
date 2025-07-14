from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product

# Rating choices (1 to 5 stars, with display symbols)
# Uses Django’s IntegerChoices for a cleaner API.
# Provides both value and a display label (with stars).
# Easily rendered in forms and admin.
class Review(models.Model):
    class Rating(models.IntegerChoices):
        ONE = 1, _('★☆☆☆☆')
        TWO = 2, _('★★☆☆☆')
        THREE = 3, _('★★★☆☆')
        FOUR = 4, _('★★★★☆')
        FIVE = 5, _('★★★★★')

    # Foreign keys to product and user
    product = models.ForeignKey(
        Product,
        # Delete review if product is deleted
        on_delete=models.CASCADE,
        # Access via product.reviews.all()
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    # Rating and comment fields
    # Star rating
    rating = models.IntegerField(choices=Rating.choices)
    # Full review text
    comment = models.TextField()
    # Timestamps
    # Set on creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Update on save
    updated_at = models.DateTimeField(auto_now=True)
    # Admin-only moderation
    # Used to hide spam/unapproved reviews
    approved = models.BooleanField(default=False)

    # Model options
    # Newest reviews first
    class Meta:
        ordering = ['-created_at']

    # Human-readable string representation
    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"

    # Get rating as visual string (used in admin and views)
    # Overrides the built-in get_FOO_display() to ensure consistent star format even if default changes.
    def get_rating_display(self):
        return dict(self.Rating.choices)[self.rating]