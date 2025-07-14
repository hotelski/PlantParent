from django.urls import path
from .views import (
    BlogPostListView,
    BlogPostDetailView,
    BlogPostCreateView,
    BlogPostUpdateView, BlogPostReactionView
)

# Allows reverse URLs like 'blog:post_detail'
app_name = 'blog'

urlpatterns = [
    path('react/', BlogPostReactionView.as_view(), name='post_react'),
    # /blog/list → list of all blog posts
    path('list', BlogPostListView.as_view(), name='post_list'),
    # /blog/<slug>/ → detail view of a single blog post
    path('<slug:slug>/', BlogPostDetailView.as_view(), name='post_detail'),
    # /blog/add-new-post → create a new blog post
    path('add-new-post', BlogPostCreateView.as_view(), name='post_create'),
    # /blog/<slug>/edit/ → edit an existing post
    path('<slug:slug>/edit/', BlogPostUpdateView.as_view(), name='post_update'),
]