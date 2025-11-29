from django.contrib import admin
from ..models import App


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_key', 'is_active', 'rate_limit', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'app_key']
    readonly_fields = ['id', 'app_key', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active', 'rate_limit')
        }),
        ('Credentials', {
            'fields': ('fcm_server_key', 'apns_cert_path', 'apns_topic', 'web_vapid_public_key', 'web_vapid_private_key'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'app_key', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make app_key readonly after creation
        if obj:  # Editing an existing object
            return self.readonly_fields
        return [field for field in self.readonly_fields if field != 'app_key']  # Allow app_key to be generated on create