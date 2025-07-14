from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, 
    AuthenticationForm, 
    PasswordChangeForm as DjangoPasswordChangeForm
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User

# This file defines four custom Django forms:
# UserRegistrationForm: registration with validations and styling
# UserLoginForm: login using email and "remember me"
# UserProfileForm: update user profile info and profile picture
# PasswordChangeForm: change password with Bootstrap styling

#  User Registration Form
class UserRegistrationForm(UserCreationForm):
    # Custom email field
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@example.com',
            'autofocus': True
        }),
        help_text=_("This will be your username for logging in.")
    )
    # First and last name fields
    first_name = forms.CharField(
        label=_("First Name"),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=True
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=True
    )
    # Password and confirmation
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Your password must contain at least 8 characters.")
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Enter the same password as before, for verification.")
    )
    # Checkbox for agreeing to terms
    terms = forms.BooleanField(
        label=_("I agree to the Terms of Service and Privacy Policy"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=True
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    # Email uniqueness validation
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))
        return email

    # Save user with normalized email
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        if commit:
            user.save()
        return user
    
    
# User Login Form
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@example.com'
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    remember_me = forms.BooleanField(
        label=_("Remember me"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Adjust field label
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = _("Email")

# User Profile Update Form
class UserProfileForm(forms.ModelForm):
    # Optional image upload
    profile_picture = forms.ImageField(
        label=_("Profile Picture"),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text=_("Upload a profile picture (max 1MB, formats: JPG, PNG, GIF)")
    )
    # Optional contact info
    phone = forms.CharField(
        label=_("Phone Number"),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=20
    )
    address = forms.CharField(
        label=_("Address"),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        }),
        required=False
    )
    city = forms.CharField(
        label=_("City"),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=100
    )
    postal_code = forms.CharField(
        label=_("Postal Code"),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=20
    )
    country = forms.CharField(
        label=_("Country"),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        max_length=100
    )
    receive_newsletter = forms.BooleanField(
        label=_("Receive newsletter and promotions"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name',
            'profile_picture',
            'phone', 
            'address', 
            'city', 
            'postal_code', 
            'country',
            'receive_newsletter'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show current image name if it exists
        if self.instance and self.instance.profile_picture:
            self.fields['profile_picture'].help_text = _(
                f"Current: {self.instance.profile_picture.name}. Upload a new image to replace it."
            )

    # Optional: delete old profile picture if changed
    def save(self, commit=True):
        if self.instance.pk and 'profile_picture' in self.changed_data:
            old_instance = User.objects.get(pk=self.instance.pk)
            if old_instance.profile_picture and old_instance.profile_picture != self.instance.profile_picture:
                old_instance.delete_old_profile_picture()
        
        return super().save(commit=commit)
    

# Password Change Form
class PasswordChangeForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        label=_("Current Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Your password must contain at least 8 characters.")
    )
    new_password2 = forms.CharField(
        label=_("New Password Confirmation"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Autofocus the old password field
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'autofocus': True})