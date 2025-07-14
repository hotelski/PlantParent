from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView

from products.models import Product
from .models import Cart, CartItem

# Show the user's cart (GET)
class CartView(LoginRequiredMixin, DetailView):
    model = Cart
    template_name = 'cart/view.html'
    
    def get_object(self):
        # Get or create a cart for the logged-in user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

# Add a product to the cart (POST)
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Get or create a cart item for the product
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        # If it already exists, increase the quantity
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        # Return JSON if the request is via AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': cart.total_quantity,
                'item_total': cart_item.quantity,
                'item_price': cart_item.total_price,
                'cart_price': cart.total_price
            })
        
        return redirect('cart:view')

# Remove an item from the cart (POST)
class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        # Make sure the item belongs to the user's cart
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user
        )
        cart_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = Cart.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'cart_total': cart.total_quantity,
                'cart_price': cart.total_price
            })
        
        return redirect('cart:view')

# Change quantity of an item (POST)
class UpdateCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user
        )
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = Cart.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'cart_total': cart.total_quantity,
                'item_total': cart_item.quantity if quantity > 0 else 0,
                'item_price': cart_item.total_price if quantity > 0 else 0,
                'cart_price': cart.total_price
            })
        
        return redirect('cart:view')