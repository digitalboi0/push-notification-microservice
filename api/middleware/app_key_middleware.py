from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib import admin
from ..models import App
import logging

logger = logging.getLogger(__name__)


class AppKeyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip authentication for admin and health check endpoints
        # Also skip static and media files
        if (
            request.path.startswith('/admin/') or 
            request.path.startswith('/api/admin/') or 
            request.path == '/health/' or 
            request.path.startswith('/static/') or 
            request.path.startswith('/media/') or
            request.path.startswith('/favicon.ico') or
            request.path.startswith('/admin/jsi18n/') or
            request.path.startswith('/admin/static/') or
            request.path.startswith('/static/admin/') or
            request.path.startswith('/api/doc/')
        ):
            return None

        # Check for app key in headers
        app_key = request.META.get('HTTP_X_APP_KEY') or request.META.get('HTTP_X_API_KEY')
        
        if not app_key:
            return JsonResponse({
                'success': False,
                'message': 'App key is required',
                'data': None
            }, status=401)

        try:
            app_instance = App.objects.get(app_key=app_key, is_active=True)
            request.app = app_instance
        except App.DoesNotExist:
            logger.warning(f"Invalid app key attempted: {app_key[:8]}...")
            return JsonResponse({
                'success': False,
                'message': 'Invalid app key',
                'data': None
            }, status=401)

        return None