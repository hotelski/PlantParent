from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

# Use the currently active user model
User = get_user_model()

class BlogPost(models.Model):
    # Title of the blog post
    title = models.CharField(max_length=200)
    # URL-friendly version of the title (unique)
    slug = models.SlugField(max_length=200, unique=True)
    # Link to the author (foreign key to custom user)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # Main content of the post
    content = models.TextField()
    # Optional image for the post
    featured_image = models.ImageField(upload_to='blog_images/')
    # Optional short summary of the post
    excerpt = models.TextField(max_length=300, blank=True)
    # Auto-set when the post is first created
    created_at = models.DateTimeField(auto_now_add=True)
    # Auto-updated every time the post is saved
    updated_at = models.DateTimeField(auto_now=True)
    # Whether the post is publicly visible
    published = models.BooleanField(default=True)

    class Meta:
        # Newest posts first
        ordering = ['-created_at']
        # Custom permissions for publishing and editing posts
        permissions = [
            ("can_publish_post", "Can publish post"),
            ("can_edit_post", "Can edit any post"),
        ]

    # Makes the admin and shell display show the title of the post.
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Return the detail page URL for this post
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # Automatically generate slug if it's not set
        if not self.slug:
            self.slug = slugify(self.title)
        # Auto-generate excerpt from content if not manually provided
        if not self.excerpt and self.content:
            self.excerpt = self.content[:300]
        # Save the model using the parent class's save method
        super().save(*args, **kwargs)


class BlogPostReaction(models.Model):
    post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # only one reaction per post per user