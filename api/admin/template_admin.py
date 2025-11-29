from django.contrib import admin
from ..models import Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'app', 'version', 'is_active', 'created_at']
    list_filter = ['app', 'is_active', 'created_at']
    search_fields = ['name', 'app__name']
    readonly_fields = ['id', 'version', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('app', 'name', 'is_active')
        }),
        ('Template Content', {
            'fields': ('title_template', 'body_template', 'subject_template', 'data_template')
        }),
        ('Metadata', {
            'fields': ('id', 'version', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make name and app readonly after creation
        if obj:  # Editing an existing object
            return self.readonly_fields + ('name', 'app')
        return self.readonly_fields