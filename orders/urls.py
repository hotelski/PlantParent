from django.urls import path
from . import views

# Enables use of 'orders:checkout', 'orders:detail', etc. in templates
app_name = 'orders'

urlpatterns = [
    # /orders/checkout/ → Page where the user confirms their order and pays
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    # /orders/history/ → List of all past orders by the current user
    path('history/', views.OrderHistoryView.as_view(), name='history'),
    # /orders/<id>/ → Detailed view of a specific order (e.g. invoice or status)
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    # /orders/success/ → Redirected here after successful Stripe payment
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    # /orders/cancel/ → Redirected here if Stripe payment is canceled
    path('cancel/', views.PaymentCancelView.as_view(), name='cancel'),
]