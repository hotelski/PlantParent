from django.conf import settings
from django.db import models

from products.models import Product

class Wishlist(models.Model):
    # One-to-one relation to a user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        # Delete wishlist if user is deleted
        on_delete=models.CASCADE,
        # Enables user.wishlist access
        related_name='wishlist'
    )
    # Timestamps for creation and updates
    # Set once on creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Update every save
    updated_at = models.DateTimeField(auto_now=True)

    # String representation
    def __str__(self):
        return f"Wishlist of {self.user.username}"

class WishlistItem(models.Model):
    # Link to a specific wishlist
    wishlist = models.ForeignKey(
        Wishlist,
        # Delete items if wishlist is deleted
        on_delete=models.CASCADE,
        # Enables wishlist.items.all()
        related_name='items'
    )
    # Link to a product
    product = models.ForeignKey(
        Product,
        # Delete item if product is deleted
        on_delete=models.CASCADE
    )
    # Timestamp for when item was added
    added_at = models.DateTimeField(auto_now_add=True)

    # Constraint: No duplicate products in one wishlist
    # Prevents the same product from being added multiple times to the same user's wishlist.
    class Meta:
        unique_together = ['wishlist', 'product']

    # String representation
    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user.username}'s wishlist"