from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from products.models import Product
from .models import Review
from .forms import ReviewForm

# Create a new review for a product
class AddReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/add.html'

    # Get the target product by slug
    def get_product(self):
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    # Add product context for use in the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.get_product()
        return context

    # Attach user and product to the review before saving
    def form_valid(self, form):
        form.instance.product = self.get_product()
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Thank you for your review! It will be visible after approval.")
        return response

    # Redirect back to product detail page
    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.kwargs['slug']})

# Allow user to edit their own review
class UpdateReviewView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/update.html'
    # Use review_id from URL instead of pk
    pk_url_kwarg = 'review_id'

    # Only allow editing own review
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    # Redirect back to the product page after update
    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'slug': self.object.product.slug})

# Allow user to delete their review
class DeleteReviewView(LoginRequiredMixin, DeleteView):
    model = Review
    pk_url_kwarg = 'review_id'
    template_name = 'reviews/delete.html'

    # Restrict deletion to the user's own review
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    # Redirect back to product page with confirmation message
    def get_success_url(self):
        messages.success(self.request, "Your review has been deleted.")
        return reverse_lazy('products:detail', kwargs={'slug': self.object.product.slug})