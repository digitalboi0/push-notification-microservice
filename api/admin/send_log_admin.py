# api/admin/send_log_admin.py
from django.contrib import admin
from ..models import SendLog


@admin.register(SendLog)
class SendLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'app', 'notification_type', 'status', 'device_platform', 
        'device_user_identifier', 'sent_at', 'created_at'
    ]
    list_filter = [
        'app', 'status', 'notification_type', 'device__platform', 
        'sent_at', 'created_at'
    ]
    search_fields = [
        'id', 'app__name', 'notification_type', 'title', 'body', 
        'device__user_identifier', 'error_message'
    ]
    readonly_fields = [
        'id', 'app', 'device', 'template', 'notification_type', 
        'title', 'body', 'subject', 'data', 'raw_request', 
        'provider_response', 'error_message', 'sent_at', 
        'delivered_at', 'read_at', 'created_at', 'updated_at'
    ]
    
    # Optional: Custom methods to display related information in list view
    def device_platform(self, obj):
        return obj.device.platform
    device_platform.short_description = 'Device Platform'
    device_platform.admin_order_field = 'device__platform' # Allows sorting

    def device_user_identifier(self, obj):
        return obj.device.user_identifier
    device_user_identifier.short_description = 'User Identifier'
    device_user_identifier.admin_order_field = 'device__user_identifier' # Allows sorting

    # Optional: Customize fieldsets for better readability
    fieldsets = (
        ('Core Information', {
            'fields': ('id', 'app', 'device', 'template', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'body', 'subject', 'data')
        }),
        ('Request & Response', {
            'fields': ('raw_request', 'provider_response', 'error_message'),
            'classes': ('collapse',) # Collapsible section
        }),
        ('Status & Timing', {
            'fields': ('status', 'sent_at', 'delivered_at', 'read_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Prevent adding logs manually through admin
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent editing logs through admin (they are read-only)
        return False

    def has_delete_permission(self, request, obj=None):
        # Optionally, allow deletion if needed, or prevent it
        # return False # Uncomment to prevent deletion
        return super().has_delete_permission(request, obj)