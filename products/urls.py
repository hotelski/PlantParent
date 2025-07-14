from django.urls import path
from . import views

#Enables namespaced URL reversing
app_name = 'products'

urlpatterns = [
    # / → Home page
    path('', views.HomeView.as_view(), name='home' ),
    # /list → Page that lists all products (possibly with filters/pagination)
    path('list', views.ProductListView.as_view(), name='list'),
    # /search/ → Product search results (handled by a function-based view)
    path('search/', views.search, name='search'),
    # /categories/ → List of all product categories
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    # /category/<slug>/ → Detail view for a specific category (shows products in it)
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),
    # /<slug>/ → Detail view for a specific product
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
]