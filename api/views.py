# api/views/documentation_views.py
from django.shortcuts import render
from django.http import Http404 # Optional: For handling missing templates gracefully

def doc(request):
    """
    Serves the documentation page (doc.html).
    """
    try:
        return render(request, "api/doc.html") # Ensure 'api/doc.html' exists in your template dirs
    except Exception as e:
        # Log the error if needed
        # import logging
        # logger = logging.getLogger(__name__)
        # logger.error(f"Error rendering doc.html: {e}")
        # Raise a 404 if the template is not found
        raise Http404("Documentation page not found.")