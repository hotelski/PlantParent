from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from blog.models import BlogPost, BlogPostReaction
from orders.models import Order
from reviews.models import Review
from .models import Category, Product
from .filters import ProductFilter

# All Products with Filtering
class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    # Show 12 products per page
    paginate_by = 12

    # Apply filters using ProductFilter
    def get_queryset(self):
        queryset = super().get_queryset().filter(available=True)
        self.filter = ProductFilter(self.request.GET, queryset=queryset)
        return self.filter.qs

    #  Pass filter instance to template for rendering the form
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

# Product Details with Related Suggestions
class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'
    # Match by slug instead of pk
    slug_url_kwarg = 'slug'

    # Show up to 4 related products from the same category
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        return context

# List of All Categories
class CategoryListView(ListView):
    model = Category
    template_name = 'products/categories.html'
    context_object_name = 'categories'

# Products in a Specific Category
class CategoryDetailView(ListView):
    model = Product
    template_name = 'products/category.html'
    context_object_name = 'products'
    paginate_by = 12

    # Get category from URL and filter products accordingly
    def get_queryset(self):
        self.category = get_object_or_404(
            Category, 
            slug=self.kwargs['slug']
        )
        return super().get_queryset().filter(
            category=self.category, 
            available=True
        )

    #  Pass the category to template for use in heading or breadcrumbs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

# Keyword Search Across Name, Description, Category
def search(request):
    # Get the query from URL params
    query = request.GET.get('q', '')
    # Search by name, description, or category name
    results = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).filter(available=True)

    # Paginate search results (12 per page)
    paginator = Paginator(results, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Render results in template
    return render(request, 'products/search.html', {
        'query': query,
        'page_obj': page_obj,
    })

# Home Page Showing Featured Products
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'products/home.html'

    # Display up to 8 featured and available products
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(featured=True, available=True)[:8]
        return context


class HomeView(TemplateView):
    template_name = "products/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Existing context...
        context['featured_products'] = Product.objects.filter(featured=True)

        # Add stats
        User = get_user_model()
        context['stats'] = {
            'users': User.objects.count(),
            'blog_posts': BlogPost.objects.count(),
            'reviews': Review.objects.count(),
            'products': Product.objects.count(),
            'categories': Category.objects.count(),
            'likes': BlogPostReaction.objects.filter(action='like').count(),
            'dislikes': BlogPostReaction.objects.filter(action='dislike').count(),
            'orders': Order.objects.count(),
        }
        return context