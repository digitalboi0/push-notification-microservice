 
# api/views/__init__.py

# Import the views from the sub-modules to make them available
from .notification_views import SendNotificationView, BulkSendNotificationView
from .device_views import DeviceRegistrationView
from .app_views import AppListView, AppDetailView
from .template_views import TemplateListView, TemplateDetailView, TemplatePreviewView
# Add other imports as you create more view files

# --- Define the 'doc' view function directly in __init__.py ---
from django.shortcuts import render
from django.http import Http404
import logging

logger = logging.getLogger(__name__)

def doc(request):
    """
    Serves the documentation page (doc.html).
    This view is intended to be mapped to a URL like /api/docs/ in api/urls.py.
    It renders the 'api/doc.html' template.
    """
    try:
        # Render the 'api/doc.html' template
        # Ensure 'api/doc.html' exists in your configured template directories
        return render(request, "api/doc.html")
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error rendering documentation template 'api/doc.html': {e}", exc_info=True)
        # Optionally, raise a 404 error if the template is not found
        # This provides a clearer error to the user if the doc page doesn't exist
        raise Http404("Documentation page not found.")

# --- End of 'doc' view definition ---

# Define what gets imported when someone does 'from api.views import *'
__all__ = [
    'SendNotificationView',
    'BulkSendNotificationView',
    'DeviceRegistrationView',
    'AppListView',
    'AppDetailView',
    'TemplateListView',
    'TemplateDetailView',
    'TemplatePreviewView',
    # Add other view classes/functions you want to expose via 'api.views'
    'doc', # Add 'doc' to the list of publicly importable names
]
