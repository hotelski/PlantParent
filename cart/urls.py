from django.urls import path
from . import views

# Allows use of namespaced URLs like cart:add or cart:view
app_name = 'cart'

urlpatterns = [
    # /cart/view/ → Shows the contents of the user's cart
    path('view/', views.CartView.as_view(), name='view'),
    # /cart/add/<product_id>/ → Adds a product to the cart by ID
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add'),
    # /cart/remove/<item_id>/ → Removes an item from the cart by cart item ID
    path('remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove'),
    # /cart/update/<item_id>/ → Updates the quantity of a specific cart item
    path('update/<int:item_id>/', views.UpdateCartView.as_view(), name='update'),
]