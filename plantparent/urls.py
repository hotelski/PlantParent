from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    # Admin interface.
    # /admin/ → Django admin panel.
    path('admin/', admin.site.urls),

    # Include URLs from each app.
    # /accounts/ → URLs defined in accounts/urls.py
    path('accounts/', include('accounts.urls')),
    # root URL ("") → products app (homepage and product listings)
    path('', include('products.urls')),
    # /cart/ → shopping cart URLs
    path('cart/', include('cart.urls')),
    # /orders/ → order processing and history
    path('orders/', include('orders.urls')),
    # /reviews/ → product review URLs
    path('reviews/', include('reviews.urls')),
    # /wishlist/ → user's wishlist
    path('wishlist/', include('wishlist.urls')),
    # /blog/ → blog-related URLs
    path('blog/', include('blog.urls')),
    # Redirect /products/ to /
    # This means that if someone visits /products/, they will be redirected to /
    path('products/', RedirectView.as_view(url='', permanent=True)),

# This appends URL patterns to serve media files (like uploaded images) when DEBUG=True.
# Example: if MEDIA_URL = '/media/', then an uploaded image at /media/uploads/image.jpg will be served correctly.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



