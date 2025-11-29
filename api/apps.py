# api/apps.py
from django.apps import AppConfig
import os # Import os module

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    
    def ready(self):
        # Import the admin module to register the models
        import api.admin
        # Import the middleware module if it defines signal handlers or similar
        import api.middleware

        import django.conf.global_settings as default_settings 
        from django.conf import settings
        import os
        

        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        
        # Create the directory if it doesn't exist
        os.makedirs(logs_dir, exist_ok=True)
        # --- End of log directory creation ---