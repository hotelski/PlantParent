from django import forms
from .models import BlogPost, Comment


class BlogPostForm(forms.ModelForm):
    class Meta:
        # Use the BlogPost model
        model = BlogPost
        # Fields included in the form
        fields = ['title', 'featured_image', 'content', 'excerpt', 'published']
        # Field customization (widgets, labels, help text)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional short summary of your post'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your post content here...'
            }),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        # Label override
        labels = {
            'published': 'Publish immediately'
        }
        # Tooltip/helper text
        help_texts = {
            'excerpt': 'A short summary that will appear in post listings'
        }

    def __init__(self, *args, **kwargs):
        # Extract custom 'user' parameter if passed
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Remove 'published' field if user doesn't have permission to publish immediately
        if self.user and not self.user.has_perm('blog.can_publish_post'):
            self.fields.pop('published', None)
        
        # Apply Bootstrap class to all input fields (except checkboxes)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

    def clean_featured_image(self):
        image = self.cleaned_data.get('featured_image')
        # Limit image size to 5MB
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Image file too large (max 5MB)")
        return image

# This form is based on the Comment model
class CommentForm(forms.ModelForm):
    class Meta:
        # Use the Comment model
        model = Comment
        # Only include the 'text' field in the form
        fields = ['text']
        # Customize how the 'text' field is rendered in HTML
        widgets = {
            'text': forms.Textarea(attrs={
                # The textarea will have 3 visible rows
                'rows': 3,
                # Text shown when empty
                'placeholder': 'Write your comment here...',
                # Bootstrap class for styling
                'class': 'form-control'
            })
        }