from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid


class Template(models.Model):
    """
    Represents a notification template with title and body.
    Templates are stored per app and can be versioned.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app = models.ForeignKey('App', on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Template name can only contain letters, numbers, and underscores'
            )
        ],
        help_text="Unique identifier for the template within the app"
    )
    title_template = models.TextField(help_text="Template for notification title with placeholders")
    body_template = models.TextField(help_text="Template for notification body with placeholders")
    subject_template = models.TextField(
        blank=True,
        help_text="Template for email subject (if applicable)"
    )
    data_template = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data to send with the notification"
    )
    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1, help_text="Template version number")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'push_templates'
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'
        unique_together = ['app', 'name', 'version']

    def __str__(self):
        return f"{self.app.name} - {self.name} (v{self.version})"

    @property
    def latest_version(self):
        """Get the latest version of this template."""
        return Template.objects.filter(
            app=self.app,
            name=self.name
        ).order_by('-version').first()