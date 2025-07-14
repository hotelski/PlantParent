from django.urls import path
from . import views

# Enables namespaced usage like 'reviews:add' in templates or redirects
app_name = 'reviews'

urlpatterns = [
    # /reviews/add/<product-slug>/ → Create a new review for the product
    path('add/<slug:slug>/', views.AddReviewView.as_view(), name='add'),
    # /reviews/update/<product-slug>/<review-id>/ → Update a specific review
    path('update/<slug:slug>/<int:review_id>/', views.UpdateReviewView.as_view(), name='update'),
    # /reviews/delete/<product-slug>/<review-id>/ → Delete a specific review
    path('delete/<slug:slug>/<int:review_id>/', views.DeleteReviewView.as_view(), name='delete'),
]