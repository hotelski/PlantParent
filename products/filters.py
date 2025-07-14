# products/filters.py
import django_filters
from .models import Product, Category

# Define a custom filter for products
class ProductFilter(django_filters.FilterSet):
    # Text search by product name (case-insensitive)
    q = django_filters.CharFilter(
        field_name='name',
        # Case-insensitive containment
        lookup_expr='icontains',
        label='Search Products'
    )
    # Filter by category (dropdown)
    category = django_filters.ModelChoiceFilter(
        # All available categories
        queryset=Category.objects.all(),
        label='Category'
    )
    # Price range filters
    min_price = django_filters.NumberFilter(
        field_name='price',
        # Greater than or equal
        lookup_expr='gte',
        label='Min Price'
    )
    max_price = django_filters.NumberFilter(
        field_name='price',
        # Less than or equal
        lookup_expr='lte',
        label='Max Price'
    )
    # Boolean filter to show only featured products
    featured = django_filters.BooleanFilter(
        field_name='featured',
        label='Featured Only'
    )

    # Meta class that binds this filter to the Product model
    # fields here are mostly for form layout — the actual behavior is defined by the individual filter fields above.
    # The min_price and max_price are used but not listed in fields, which is allowed.
    class Meta:
        model = Product
        fields = ['q', 'category', 'featured']