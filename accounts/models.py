from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from PIL import Image
import uuid


class UserManager(BaseUserManager):
    use_in_migrations = True

    # Internal method to create and save a User
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Creates a regular (non-staff) user
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    # Creates a superuser with admin permissions
    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

# Ensure uploaded image is less than 1MB
def validate_image_size(image):
    file_size = image.size
    limit_mb = 1
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f'Image size cannot exceed {limit_mb}MB. Current size: {file_size / (1024*1024):.2f}MB')

# Ensure the file extension is valid
def validate_image_format(image):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported file format. Please use: {", ".join(valid_extensions)}')

# Generate a unique upload path for each user's profile picture
def user_profile_picture_path(instance, filename):
    """Generate upload path for user profile pictures"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profile_pictures', str(instance.id), filename)

class User(AbstractUser):
    # Remove username field
    username = None
    email = models.EmailField(_('email address'), unique=True)
    # Extra fields
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_format],
        help_text=_('Upload a profile picture (max 1MB, formats: JPG, PNG, GIF)')
    )
    receive_newsletter = models.BooleanField(default=False)

    # Use email as login field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Assign the custom user manager
    objects = UserManager()

    class Meta:
        permissions = [
            ("can_publish_post", "Can publish blog posts without approval"),
            ("can_edit_all_posts", "Can edit any blog post (not just own)"),
        ]

    def __str__(self):
        # Display email when printing user
        return self.email

    # Resize the uploaded profile picture if it's too large
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.profile_picture:
            try:
                img = Image.open(self.profile_picture.path)
                
                # Resize image if it's too large (maintain aspect ratio)
                max_size = (300, 300)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(self.profile_picture.path, optimize=True, quality=85)
            except Exception as e:
                # Silently ignore errors in image processing
                pass

    # Return profile picture URL or None if not set
    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return None

    # Delete the old profile picture file from disk
    def delete_old_profile_picture(self):
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'