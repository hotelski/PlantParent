import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView
)

from cart.models import Cart, CartItem
from .models import Order, OrderItem

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

# Shows all past orders for the current user
class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/history.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        # Only show orders belonging to the current user
        return super().get_queryset().filter(
            user=self.request.user
        ).order_by('-created_at')

# Show details of a single order
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        # Prevent users from viewing other users’ orders
        return super().get_queryset().filter(
            user=self.request.user
        )

# Create order & initiate Stripe Checkout
class CheckoutView(LoginRequiredMixin, CreateView):
    template_name = 'orders/checkout.html'
    # Fallback; not used due to redirect
    success_url = reverse_lazy('orders:history')
    model = Order
    # Form fields are not generated from model; handled manually
    fields = []

    # Show checkout page (only if cart not empty)
    def get(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty!")
            return redirect('cart:view')
        return super().get(request, *args, **kwargs)

    # Create Order, OrderItems, and Stripe Checkout Session
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        
        order = Order.objects.create(
            user=request.user,
            shipping_address=request.POST.get('address'),
            shipping_city=request.POST.get('city'),
            shipping_postal_code=request.POST.get('postal_code'),
            shipping_country=request.POST.get('country'),
            total_paid=cart.total_price
        )
        # Add cart items as order items and reduce stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            item.product.stock -= item.quantity
            item.product.save()

        # Build Stripe line items
        line_items = []
        for item in cart.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item.product.name,
                    },
                    # Convert to cents
                    'unit_amount': int(item.product.price * 100),
                },
                'quantity': item.quantity,
            })

        # Create Stripe Checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse_lazy('orders:success')
            ),
            cancel_url=request.build_absolute_uri(
                reverse_lazy('orders:cancel')
            ),
            customer_email=request.user.email,
            metadata={'order_id': order.id}
        )
        # Clear cart and redirect to Stripe
        # Empty the cart after initiating checkout
        cart.items.all().delete()
        # Redirect to Stripe payment page
        return redirect(checkout_session.url)

# After successful payment
class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/success.html'

# If user cancels payment
class PaymentCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'orders/cancel.html'