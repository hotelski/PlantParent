from django.urls import path
from . import views

# Namespace to avoid URL name collisions across apps
app_name = 'wishlist'

urlpatterns = [
    # View the user's wishlist
    path('view', views.WishlistView.as_view(), name='view'),
    # Add a product to the wishlist
    path('add/<int:product_id>/', views.AddToWishlistView.as_view(), name='add'),
    # Remove a product from the wishlist
    path('remove/<int:product_id>/', views.RemoveFromWishlistView.as_view(), name='remove'),
    # Move a product from wishlist to shopping cart
    path('move-to-cart/<int:product_id>/', views.MoveToCartView.as_view(), name='move_to_cart'),
]