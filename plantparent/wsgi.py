"""
WSGI config for plantparent project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Set the default settings module for Django
# This tells Django where to find the project's settings.py file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plantparent.settings')

# Create the WSGI application object that the WSGI server (e.g., Gunicorn, uWSGI) will use to run the project
application = get_wsgi_application()
