from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product

# Order model
class Order(models.Model):
    # Order status options (using Django's TextChoices)
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')

    # User who placed the order
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # Delete order if user is deleted
        on_delete=models.CASCADE,
        # Access with user.orders.all()
        related_name='orders'
    )
    # Status of the order (with default value)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    # Timestamps for creation and update
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Shipping address fields
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    # Stripe payment ID and total paid
    stripe_payment_intent = models.CharField(max_length=100, blank=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)

    # Meta and string representation
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    # Property to get total item count
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

# OrderItem model – individual products in an order
class OrderItem(models.Model):
    #  Link to Order
    order = models.ForeignKey(
        Order,
        # Delete item if order is deleted
        on_delete=models.CASCADE,
        # Access via order.items.all()
        related_name='items'
    )
    # Link to Product (protect so product can't be deleted)
    product = models.ForeignKey(
        Product,
        # Prevent deleting products used in orders
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    # Price and quantity at the time of order
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    # String representation
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order #{self.order.id}"

    # Calculate total price for this line item
    @property
    def total_price(self):
        return self.price * self.quantity