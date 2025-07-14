from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Review

# Custom review submission form
class ReviewForm(forms.ModelForm):
    # Star-based rating options (1 to 5)
    RATING_CHOICES = [
        (1, '★☆☆☆☆ - Poor'),
        (2, '★★☆☆☆ - Fair'),
        (3, '★★★☆☆ - Good'),
        (4, '★★★★☆ - Very Good'),
        (5, '★★★★★ - Excellent'),
    ]
    # Rating field as radio buttons
    # Uses stars in the choice labels
    # Rendered as radio buttons
    # Fully translatable label
    rating = forms.ChoiceField(
        label=_("Your Rating"),
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        required=True
    )

    # Comment field with styling and placeholder
    # Required field for user feedback
    # Limited to 1000 characters
    # Uses Bootstrap styling (form-control)
    comment = forms.CharField(
        label=_("Your Review"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _('Share your experience with this product...')
        }),
        required=True,
        max_length=1000
    )

    # Model binding and field labels
    # Maps form fields directly to the Review model
    # Custom labels can be translated
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': _('Rating'),
            'comment': _('Review')
        }

    # Clean method for comment field
    # Ensures the user writes something meaningful (≥10 characters)
    # Removes leading/trailing whitespace before checking length
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment.strip()) < 10:
            raise ValidationError(_('Please provide a more detailed review (at least 10 characters).'))
        return comment

    # Form customization on init (styling radio buttons)
    # Enhances radio buttons with extra styling using Bootstrap classes
    # Makes the form more visually appealing and consistent with site design
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({
            'class': 'form-check-input',
            'style': 'margin-right: 5px;'
        })