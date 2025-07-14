from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import BlogPost, BlogPostReaction
from .forms import BlogPostForm
from django.contrib import messages
import json

# List all published posts
class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    # Filter only published posts
    def get_queryset(self):
        return BlogPost.objects.filter(published=True)

    # Add permission-based context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            context['can_edit_all'] = user.has_perm('blog.can_edit_post') or user.is_superuser
            context['can_publish'] = user.has_perm('blog.can_publish_post') or user.is_superuser
            context['can_add_post'] = user.has_perm('blog.add_blogpost') or user.is_superuser
        
        return context

# View a single post
class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'

    # Show only published posts
    def get_queryset(self):
        return BlogPost.objects.filter(published=True)

    # Add edit permission info to context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        post = self.get_object()

        context['like_count'] = post.reactions.filter(action='like').count()
        context['dislike_count'] = post.reactions.filter(action='dislike').count()
        
        if user.is_authenticated:
            context['can_edit_all'] = user.has_perm('blog.can_edit_post') or user.is_superuser
        
        return context


# Create a new post
class BlogPostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:post_list')

    # Pass the user to the form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # Set author and show message
    def form_valid(self, form):
        # Assign the current user as the author
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            "Your post has been successfully created!" + 
            (" It's pending approval." if not form.instance.published else "")
        )
        return response


# Edit an existing post
class BlogPostUpdateView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/post_form.html'

    # Pass user to the form
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    # Redirect to the post detail page after saving
    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Show success/warning messages depending on publish status
        if 'published' in form.changed_data:
            if form.instance.published:
                messages.success(self.request, "Post has been published!")
            else:
                messages.warning(self.request, "Post has been unpublished.")
        else:
            messages.success(self.request, "Post updated successfully!")
        
        return response


@method_decorator(csrf_exempt, name='dispatch')
class BlogPostReactionView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Login required'}, status=403)

        try:
            data = json.loads(request.body)
            post_id = data.get('post_id')
            action = data.get('action')
        except:
            return JsonResponse({'success': False}, status=400)

        if action not in ['like', 'dislike']:
            return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)

        post = BlogPost.objects.filter(id=post_id).first()
        if not post:
            return JsonResponse({'success': False, 'message': 'Post not found'}, status=404)

        reaction, created = BlogPostReaction.objects.get_or_create(
            post=post, user=request.user,
            defaults={'action': action}
        )

        if not created:
            if reaction.action == action:
                # Remove reaction (toggle off)
                reaction.delete()
            else:
                # Update reaction
                reaction.action = action
                reaction.save()

        return JsonResponse({
            'success': True,
            'likes': post.reactions.filter(action='like').count(),
            'dislikes': post.reactions.filter(action='dislike').count()
        })
