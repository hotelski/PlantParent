from django.conf import settings
from django.db import models

from products.models import Product

class Cart(models.Model):
    # One cart per user (One-to-One relationship)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        # Delete cart if user is deleted
        on_delete=models.CASCADE,
        # Allows access via user.cart
        related_name='cart'
    )
    # Set on creation
    created_at = models.DateTimeField(auto_now_add=True)
    # Update every time the cart changes
    updated_at = models.DateTimeField(auto_now=True)

    # Calculate total price of all items in the cart
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    # Calculate total quantity of all items
    @property
    def total_quantity(self):
        print(sum(item.quantity for item in self.items.all()))
        return sum(item.quantity for item in self.items.all())

    # String representation
    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    # Each item belongs to a cart
    cart = models.ForeignKey(
        Cart,
        # Delete item if cart is deleted
        on_delete=models.CASCADE,
        # Allows access via cart.items
        related_name='items'
    )
    # Reference to a product
    product = models.ForeignKey(
        Product,
        # Delete item if product is deleted
        on_delete=models.CASCADE
    )
    # Quantity of this product in the cart
    quantity = models.PositiveIntegerField(default=1)
    # Timestamp when this item was added
    added_at = models.DateTimeField(auto_now_add=True)

    # Total price for this cart item
    @property
    def total_price(self):
        return self.product.price * self.quantity

    # String representation
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"