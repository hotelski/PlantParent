from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView

from products.models import Product
from .models import Wishlist, WishlistItem
from cart.models import Cart, CartItem

# Show the user's wishlist
class WishlistView(LoginRequiredMixin, DetailView):
    model = Wishlist
    template_name = 'wishlist/view.html'
    
    def get_object(self):
        # # Get or create a wishlist for the current user
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist

# Add product to wishlist
class AddToWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        # Get the product or return 404 if not found
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Create wishlist item only if it doesn't exist
        wishlist_item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product
        )

        # Return a JSON response if request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'action': 'added',
                'wishlist_count': wishlist.items.count()
            })

        # Otherwise, redirect to the wishlist page
        return redirect('wishlist:view')

# Remove product from wishlist
class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist = get_object_or_404(Wishlist, user=request.user)

        # Delete the wishlist item if it exists
        WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product
        ).delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'action': 'removed',
                'wishlist_count': wishlist.items.count()
            })
        
        return redirect('wishlist:view')

# Move item from wishlist to shopping cart
class MoveToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist = get_object_or_404(Wishlist, user=request.user)

        # Step 1: Remove item from wishlist
        WishlistItem.objects.filter(
            wishlist=wishlist,
            product=product
        ).delete()

        # Step 2: Add product to cart (create cart if needed)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        # If item already exists in cart, increase quantity
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'action': 'moved',
                'wishlist_count': wishlist.items.count(),
                'cart_count': cart.total_quantity
            })
        
        return redirect('cart:view')