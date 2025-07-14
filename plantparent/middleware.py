# For extracting and formatting the traceback of exceptions.
import traceback
# To get current exception info and Python version.
import sys
from datetime import datetime
# Used to render a template.
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.exceptions import PermissionDenied
import logging

# Set up a logger for recording errors.
logger = logging.getLogger(__name__)

# Custom middleware to show debug error page for all exceptions and 404 errors.
# Only works when DEBUG=True.
class DebugErrorMiddleware:
    # __init__ method – required for all middleware.
    # Stores the next middleware or view to be called.
    def __init__(self, get_response):
        self.get_response = get_response

    # __call__ method – runs on each request.
    def __call__(self, request):
        # Call the next middleware or view.
        response = self.get_response(request)
        
        # If response is 404, and we're in debug mode, show custom page.
        if response.status_code == 404 and settings.DEBUG:
            return self.handle_404(request)

        # Return the original response if no 404.
        return response

    # Custom 404 handler for debug mode.
    def handle_404(self, request):
        context = {
            'exception_type': 'PageNotFound',
            'exception_value': 'The requested page does not exist',
            'filename': '',
            'lineno': '',
            'traceback': '',
            'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'request': request,
            'settings': settings,
            'python_version': sys.version,
            'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            'requested_path': request.path,
        }
        
        try:
            # Render debug_error.html
            return render(request, 'debug_error.html', context, status=404)
        except Exception as template_error:
            logger.error(f"Error rendering 404 template: {template_error}")
            # Fallback plain HTML if template fails
            return HttpResponse(
                f"""
                <h1>404 Page Not Found</h1>
                <p>The requested URL {request.path} was not found on this server.</p>
                <p><strong>Template Error:</strong> {template_error}</p>
                """, 
                status=404
            )

    # Handles unexpected exceptions from views.
    def process_exception(self, request, exception):
        if not settings.DEBUG:
            # Do not interfere when not in debug mode.
            return None 
        
        # Skip handling for Http404 and PermissionDenied if you want default behavior
        if isinstance(exception, Http404):
            # Use custom 404 handler.
            return self.handle_404(request)
        if isinstance(exception, PermissionDenied):
            # Let Django handle PermissionDenied normally.
            return None

        # Extracts traceback details.
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        full_traceback = ''.join(tb_lines)
        tb = exc_traceback
        # Go to the last traceback frame.
        while tb.tb_next:
            tb = tb.tb_next

        # Extract filename.
        filename = tb.tb_frame.f_code.co_filename
        # Extract line number.
        lineno = tb.tb_lineno
        # Build context and render debug page.
        logger.error(f"Exception in {request.path}: {exception}\n{full_traceback}")
        context = {
            'exception_type': exc_type.__name__ if exc_type else 'Unknown',
            'exception_value': str(exc_value) if exc_value else 'No details',
            'filename': filename,
            'lineno': lineno,
            'traceback': full_traceback,
            'error_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'request': request,
            'settings': settings,
            'python_version': sys.version,
            'django_version': getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            'requested_path': request.path,
        }

        # Fallback if rendering fails.
        try:
            return render(request, 'debug_error.html', context, status=500)
        except Exception as template_error:
            logger.error(f"Error rendering debug template: {template_error}")
            return HttpResponse(
                f"""
                <h1>Error occurred</h1>
                <p><strong>Original Error:</strong> {exception}</p>
                <p><strong>Template Error:</strong> {template_error}</p>
                <pre>{full_traceback}</pre>
                """, 
                status=500
            )