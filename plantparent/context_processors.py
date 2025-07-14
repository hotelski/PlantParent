# Imports the Cart model from the cart app.
from cart.models import Cart
# Imports the Wishlist model from the wishlist app.
from wishlist.models import Wishlist

# Context processor for the shopping cart.
def cart_context(request):
    # Initialize an empty dictionary to store context data.
    context = {}
    # Only proceed if the user is logged in.
    if request.user.is_authenticated:
        # Get the first cart belonging to the user.
        cart = Cart.objects.filter(user=request.user).first()
        # Add the cart to the context under the key 'cart'.
        context['cart'] = cart
    # Return the context dictionary.
    return context

# Context processor for the wishlist.
def wishlist_context(request):
    # Initialize an empty dictionary.
    context = {}
    # Only for authenticated users.
    if request.user.is_authenticated:
        # Get the user's wishlist, or create one if it doesn't exist.
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        # Add the wishlist to the context.
        context['wishlist'] = wishlist
    # Return the context.
    return context