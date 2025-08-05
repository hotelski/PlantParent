from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, render, get_object_or_404
from .models import BlogPost, BlogPostReaction, Comment
from .forms import BlogPostForm, CommentForm
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
    # This view shows the detail of a single BlogPost
    model = BlogPost
    # HTML template used for rendering
    template_name = 'blog/post_detail.html'
    # The object will be referred to as 'post' in the template
    context_object_name = 'post'
    # Uses the 'slug' field to retrieve the post
    slug_field = 'slug'

    # Return all posts for admins/editors, but only published posts for others
    def get_queryset(self):
        if self.request.user.is_authenticated and (
                self.request.user.is_superuser or self.request.user.has_perm('blog.can_edit_post')):
            return BlogPost.objects.all()
        return BlogPost.objects.filter(published=True)

    # Add edit permission info to context
    # Add additional data to the template context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        post = self.get_object()

        # Pass like/dislike counts to the template
        context['like_count'] = post.reactions.filter(action='like').count()
        context['dislike_count'] = post.reactions.filter(action='dislike').count()
        # Pass all comments, and the blank comment form
        context['comments'] = post.comments.order_by('-created_at')
        context['comment_form'] = CommentForm()

        # Add a flag if the user has edit permissions
        if user.is_authenticated:
            context['can_edit_all'] = user.has_perm('blog.can_edit_post') or user.is_superuser

        return context

    # Handle POST requests for creating, editing, or deleting comments
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        post = self.object
        context = self.get_context_data()

        # Handle new comment submission
        if 'submit_comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid() and request.user.is_authenticated:
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                # Redirect to the new comment
                return HttpResponseRedirect(post.get_absolute_url() + f'#comment-{comment.pk}')

        # Handle comment edit
        elif 'submit_edit' in request.POST:
            comment_id = request.POST.get("comment_id")
            comment = get_object_or_404(Comment, pk=comment_id, post=post)
            # Only author, staff, or superuser can edit
            if comment.author == request.user or request.user.is_staff or request.user.is_superuser:
                form = CommentForm(request.POST, instance=comment)
                if form.is_valid():
                    form.save()
                    # Redirect to the updated comment
                    return HttpResponseRedirect(post.get_absolute_url() + f'#comment-{comment.pk}')

        # Handle comment delete
        elif 'submit_delete' in request.POST:
            comment_id = request.POST.get("comment_id")
            comment = get_object_or_404(Comment, pk=comment_id, post=post)
            # Only staff or superuser can delete comments
            if request.user.is_staff or request.user.is_superuser:
                comment.delete()
                return HttpResponseRedirect(post.get_absolute_url() + '#comments')

        # Fallback if none matched or form invalid
        return render(request, self.template_name, context)

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
