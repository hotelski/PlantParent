# blog/management/commands/setup_blog_permissions.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import BlogPost

# Define the command class
# Help message shown with --help
class Command(BaseCommand):
    help = 'Creates blog author and editor groups with permissions'

    # Main logic inside the handle() method
    def handle(self, *args, **options):
        # Create or get the groups
        # get_or_create ensures the groups won't be duplicated if the command runs multiple times
        author_group, created = Group.objects.get_or_create(name='Blog Authors')
        editor_group, created = Group.objects.get_or_create(name='Blog Editors')
        
        # Get permissions tied to the BlogPost model
        # Built-in permissions: add_blogpost, change_blogpost
        # Custom permissions (defined in BlogPost.Meta): can_publish_post, can_edit_post
        content_type = ContentType.objects.get_for_model(BlogPost)
        
        add_permission = Permission.objects.get(
            codename='add_blogpost',
            content_type=content_type,
        )
        change_permission = Permission.objects.get(
            codename='change_blogpost',
            content_type=content_type,
        )
        publish_permission = Permission.objects.get(
            codename='can_publish_post',
            content_type=content_type,
        )
        edit_any_permission = Permission.objects.get(
            codename='can_edit_post',
            content_type=content_type,
        )
        
        # Assign permissions to groups
        author_group.permissions.add(add_permission, change_permission)
        # Blog Authors: can add and edit their own posts
        # Blog Editors: can do everything authors can, plus publish and edit any post
        editor_group.permissions.add(
            add_permission, 
            change_permission, 
            publish_permission,
            edit_any_permission
        )

        # Output success message
        self.stdout.write(self.style.SUCCESS('Successfully set up blog permissions'))