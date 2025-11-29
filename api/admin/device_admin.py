from django.contrib import admin
from ..models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['app', 'platform', 'user_identifier', 'is_active', 'created_at']
    list_filter = ['app', 'platform', 'is_active', 'created_at']
    search_fields = ['user_identifier', 'device_token']
    readonly_fields = ['id', 'created_at', 'updated_at', 'push_token_updated_at']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('app', 'platform', 'user_identifier', 'device_token', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'push_token_updated_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )