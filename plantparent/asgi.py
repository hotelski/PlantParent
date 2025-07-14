"""
ASGI config for plantparent project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Sets the default Django settings module for the 'asgi' environment.
# This tells Django where to find the settings.py file.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plantparent.settings')

# Creates the ASGI application object that will be used by any ASGI server.
application = get_asgi_application()
