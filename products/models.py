from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    # Category name
    name = models.CharField(max_length=100)
    # URL-safe identifier
    slug = models.SlugField(max_length=100, unique=True)
    # Optional description
    description = models.TextField(blank=True)
    # Optional image
    image = models.ImageField(upload_to='categories/', blank=True)
    
    class Meta:
        # Fixes plural name in admin
        verbose_name_plural = "Categories"
        # Default ordering A-Z
        ordering = ['name']

    # String representation
    def __str__(self):
        return self.name

    # Get category detail URL
    def get_absolute_url(self):
        return reverse('products:category', args=[self.slug])

    # Auto-generate slug on save
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# Product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Link to category (nullable)
    category = models.ForeignKey(
        Category,
        # Allows category.products.all()
        related_name='products', 
        on_delete=models.SET_NULL, 
        null=True
    )
    # Image and inventory & Timestamps
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)

    # Metadata and indexing
    class Meta:
        # Newest first
        ordering = ['-created']
        indexes = [
            # Speed up detail view queries
            models.Index(fields=['id', 'slug']),
            # Useful for searching
            models.Index(fields=['name']),
            # Useful for sorting by newest
            models.Index(fields=['-created']),
        ]

    # String and URL representation
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug])

    # Auto-fill slug and short_description on save
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.short_description and self.description:
            self.short_description = self.description[:300]
        super().save(*args, **kwargs)